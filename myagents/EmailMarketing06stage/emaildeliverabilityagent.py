# 📁 agents/email_deliverability_agent.py

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

# ========== Input Schema ==========
class DeliverabilityCheckInput(BaseModel):
    domain: str
    spf_record: str
    dkim_record: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Analyze the SPF and DKIM records for {self.domain}.\n"
                f"SPF: {self.spf_record}\n"
                f"DKIM: {self.dkim_record}\n"
                "Explain if they are correctly configured and suggest improvements."
            )
        }]

# ========== Tool Function ==========
@function_tool
def check_deliverability(domain: str, spf_record: str, dkim_record: str) -> str:
    """
    Checks SPF and DKIM configuration for email deliverability.
    """
    try:
        prompt = DeliverabilityCheckInput(
            domain=domain,
            spf_record=spf_record,
            dkim_record=dkim_record
        ).to_prompt()

        result = asyncio.run(Runner.run(get_deliverability_agent(), prompt))
        return result.final_output or "⚠️ No suggestions returned."
    except Exception as e:
        return f"❌ Error checking deliverability: {str(e)}"

# ========== Agent ==========

def get_deliverability_agent() -> Agent:
    return Agent(
        name="EmailDeliverabilityAgent",
        instructions=(
            "You're an expert in email deliverability and DNS configuration.\n"
            "Your task is to review SPF and DKIM records for potential issues.\n\n"
            "✅ Rules:\n"
            "- Identify misconfigurations.\n"
            "- Recommend actionable fixes (e.g., missing include, invalid syntax).\n"
            "- Mention impact on inbox placement if applicable.\n\n"
            "⚠️ If records are missing or malformed, call it out clearly."
        ),
        tools=[check_deliverability],
        model=model
    )

# ========== Tool Export ==========

def get_deliverability_tool():
    return get_deliverability_agent().as_tool(
        tool_name="email_deliverability_checker",
        tool_description="Analyzes SPF and DKIM records for email configuration issues."
    )

# ========== Manual Runner (optional testing) ==========
async def run_deliverability_check(domain: str, spf_record: str, dkim_record: str) -> str:
    try:
        prompt = DeliverabilityCheckInput(
            domain=domain,
            spf_record=spf_record,
            dkim_record=dkim_record
        ).to_prompt()
        result = await Runner.run(get_deliverability_agent(), prompt)
        return result.final_output or "⚠️ Deliverability check failed."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== CLI (Manual test) ==========
if __name__ == "__main__":
    async def main():
        print("📧 Email Deliverability Agent Ready!")
        while True:
            domain = input("🌐 Enter domain (or 'exit'): ").strip()
            if domain.lower() in ["exit", "quit"]:
                break
            spf = input("🛡️ Enter SPF record: ").strip()
            dkim = input("🔐 Enter DKIM record: ").strip()

            output = await run_deliverability_check(domain, spf, dkim)
            print("✅ Output:\n", output)

    asyncio.run(main())
