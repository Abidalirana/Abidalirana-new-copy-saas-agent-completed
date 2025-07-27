import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

# ========== Configuration ==========
load_dotenv()
set_tracing_disabled(True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# ========== Schema ==========
class EmailReportInput(BaseModel):
    campaign_id: str
    stats_json: str  # Assume we pass a stringified JSON with stats (open, click, bounce etc.)

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Generate a performance summary for the following email campaign stats:\n"
                f"Campaign ID: {self.campaign_id}\n"
                f"Stats JSON:\n{self.stats_json}\n\n"
                "Summarize opens, clicks, bounces, replies, and unsubscribes in a short readable format. "
                "Highlight performance and suggest improvements."
            )
        }]

# ========== Tool ==========
@function_tool
def generate_email_report(campaign_id: str, stats_json: str) -> str:
    """
    Summarizes key email campaign metrics into a report.
    """
    try:
        prompt = EmailReportInput(
            campaign_id=campaign_id,
            stats_json=stats_json
        ).to_prompt()

        result = asyncio.run(Runner.run(email_report_agent, prompt))
        return result.final_output or "⚠️ No report generated."
    except Exception as e:
        return f"❌ Error generating report: {str(e)}"

# ========== Agent ==========
email_report_agent = Agent(
    name="EmailReportGeneratorAgent",
    instructions=(
        "You're an email campaign analyst.\n"
        "Your job is to review JSON performance data for a campaign and write a short summary.\n\n"
        "✅ Rules:\n"
        "- Include open rate, click rate, bounces, replies, and unsubscribes.\n"
        "- Suggest improvements if any metric is low.\n"
        "- Keep summary under 150 words.\n\n"
        "⚠️ If data is incomplete or malformed, return a warning."
    ),
    tools=[generate_email_report],
    model=model
)

# ========== Automation Entry ==========
async def run_email_report_agent(campaign_id: str, stats_json: str) -> str:
    try:
        prompt = EmailReportInput(
            campaign_id=campaign_id,
            stats_json=stats_json
        ).to_prompt()
        result = await Runner.run(email_report_agent, prompt)
        return result.final_output or "⚠️ Report generation failed."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== Tool Export ==========
def get_email_report_tool():
    return email_report_agent.as_tool(
        tool_name="email_report_generator",
        tool_description="Generates a summary report of email campaign metrics like open rate, click rate, bounces, and suggestions."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("📊 Email Report Generator Agent Ready!")
        while True:
            campaign_id = input("📧 Enter Campaign ID (or 'exit'): ").strip()
            if campaign_id.lower() in ["exit", "quit"]:
                break
            stats_json = input("📄 Paste JSON stats: ").strip()

            try:
                prompt = EmailReportInput(
                    campaign_id=campaign_id,
                    stats_json=stats_json
                ).to_prompt()
                result = await Runner.run(email_report_agent, prompt)
                print("✅ Campaign Summary:\n", result.final_output)
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(main())
