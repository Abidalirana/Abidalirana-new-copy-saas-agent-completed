# adreportgeneratoragent.py

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
class AdReportInput(BaseModel):
    platform: str
    campaign_name: str
    timeframe: str

    def to_messages(self):
        return [
            {
                "role": "user",
                "content": (
                    f"Generate a performance report for the campaign '{self.campaign_name}' on {self.platform} "
                    f"for the timeframe: {self.timeframe}. Include CTR, CPC, CPM, and conversion data."
                )
            }
        ]

# ========== Tools ==========
@function_tool
def generate_ad_report(platform: str, campaign_name: str, timeframe: str) -> str:
    """
    Create a simulated ad performance report based on platform, campaign name, and timeframe.
    """
    try:
        if not platform or not campaign_name or not timeframe:
            raise ValueError("Missing required report input.")

        return (
            f"📊 Ad Campaign Report\n"
            f"Platform: {platform}\n"
            f"Campaign: {campaign_name}\n"
            f"Timeframe: {timeframe}\n\n"
            f"🔍 Performance Metrics:\n"
            f"- CTR: 3.4%\n"
            f"- CPC: $1.15\n"
            f"- CPM: $12.60\n"
            f"- Conversions: 154\n"
            f"- ROAS: 3.8x\n\n"
            f"✅ Summary:\n"
            f"This campaign is performing above average on {platform}. CTR and conversion rates are healthy. "
            f"Consider increasing the budget or testing new creative for scaling."
        )

    except Exception as e:
        return (
            f"⚠️ Error generating ad report: {str(e)}\n"
            "Fallback: Pull campaign performance data manually from Ads Manager or Analytics tool."
        )

# ========== Agent ==========
ad_report_agent = Agent(
    name="AdReportGeneratorAgent",
    instructions=(
        "You are an Ad Report Generator Agent. Your job is to summarize ad performance based on platform, campaign name, and timeframe.\n\n"
        "📈 Reporting Rules:\n"
        "- Include key metrics: CTR, CPC, CPM, Conversions, ROAS.\n"
        "- Format clearly and use bullet points.\n"
        "- Add a short summary at the end with recommendations.\n\n"
        "✅ Output Format:\n"
        "- Campaign Metadata\n"
        "- Performance Metrics\n"
        "- Summary/Insights"
    ),
    tools=[generate_ad_report],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📊 Ad Report Generator Agent Ready!")
        while True:
            platform = input("🧱 Enter Ad Platform (Meta, Google, etc.): ").strip()
            campaign_name = input("📢 Enter Campaign Name: ").strip()
            timeframe = input("🕒 Enter Timeframe (e.g., last 7 days): ").strip()

            if any(x.lower() in ["exit", "quit"] for x in [platform, campaign_name, timeframe]):
                print("👋 Exiting. Bye!")
                break

            if not platform or not campaign_name or not timeframe:
                print("⚠️ Please provide all inputs.\n")
                continue

            input_data = AdReportInput(
                platform=platform,
                campaign_name=campaign_name,
                timeframe=timeframe
            ).to_messages()

            try:
                result = await Runner.run(ad_report_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Report generation failed. Fallback to manual export from ads dashboard. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_ad_report_agent(platform: str, campaign_name: str, timeframe: str) -> str:
    """
    Programmatic runner for AdReportGeneratorAgent – used by orchestrator.
    """
    if not platform or not campaign_name or not timeframe:
        return "⚠️ Missing required data for ad report."

    input_data = AdReportInput(
        platform=platform,
        campaign_name=campaign_name,
        timeframe=timeframe
    ).to_messages()

    try:
        result = await Runner.run(ad_report_agent, input_data)
        return result.final_output or "⚠️ No output generated. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception occurred: {e}\n"
            "Fallback: Use platform-native reporting and analytics."
        )
#===========================
# ========== Tool Export Function ========== #
def get_ad_report_generator_agent_tool():
    """
    Exposes AdReportGeneratorAgent as a tool for orchestrators.
    """
    return ad_report_agent.as_tool(
        tool_name="ad_report_generator_agent",
        tool_description="Generates a performance report for an ad campaign including CTR, CPC, CPM, conversions, and insights."
    )
