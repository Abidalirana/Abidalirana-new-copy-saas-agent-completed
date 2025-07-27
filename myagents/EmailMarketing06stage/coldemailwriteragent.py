# coldemailwriteragent.py

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
class ColdEmailInput(BaseModel):
    company: str
    product: str
    target_audience: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Write a professional cold email introducing {self.company}'s {self.product} to a "
                f"{self.target_audience}. Make it concise, persuasive, and actionable."
            )
        }]

# ========== Tool ==========
@function_tool
def write_cold_email(company: str, product: str, target_audience: str) -> str:
    """
    Generates a cold outreach email tailored to a specific audience.
    """
    try:
        prompt = ColdEmailInput(
            company=company,
            product=product,
            target_audience=target_audience
        ).to_prompt()

        result = asyncio.run(Runner.run(cold_email_agent, prompt))
        return result.final_output or "⚠️ No email generated. Try different input."
    except Exception as e:
        return f"❌ Error generating cold email: {str(e)}"

# ========== Agent ==========
cold_email_agent = Agent(
    name="ColdEmailWriterAgent",
    instructions=(
        "You're an expert email copywriter. Your task is to write short, effective cold emails.\n\n"
        "✅ Rules:\n"
        "- Focus on benefits, not features.\n"
        "- Always end with a strong CTA.\n"
        "- Personalize tone for the audience.\n"
        "- Output must be max 150 words.\n\n"
        "⚠️ If any input field is missing or unclear, respond with a warning."
    ),
    tools=[write_cold_email],
    model=model
)

# ========== Automation Entry ==========
async def run_cold_email_writer(company: str, product: str, target_audience: str) -> str:
    try:
        input_data = ColdEmailInput(
            company=company,
            product=product,
            target_audience=target_audience
        ).to_prompt()
        result = await Runner.run(cold_email_agent, input_data)
        return result.final_output or "⚠️ Cold email generation failed."
    except Exception as e:
        return f"❌ Automation Error: {e}"

# ========== Tool Export ==========
def get_coldemail_writer_tool():
    return cold_email_agent.as_tool(
        tool_name="cold_email_writer",
        tool_description="Generates a concise and persuasive cold email tailored to a company's product and audience."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("📩 Cold Email Writer Ready!")
        while True:
            company = input("🏢 Enter company name (or 'exit'): ").strip()
            if company.lower() in ["exit", "quit"]:
                break
            product = input("📦 Enter product/service: ").strip()
            audience = input("🎯 Target audience: ").strip()

            prompt = ColdEmailInput(company=company, product=product, target_audience=audience).to_prompt()
            try:
                result = await Runner.run(cold_email_agent, prompt)
                print("✅ Generated Email:\n", result.final_output)
            except Exception as e:
                print(f"❌ Failed: {e}")
    asyncio.run(main())
