import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List

# ========== Config ==========
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
class EmailValidationInput(BaseModel):
    emails: List[str]

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Validate the following email addresses:\n"
                f"{', '.join(self.emails)}\n\n"
                "For each email, return whether it's valid or not, and explain why if it's invalid "
                "(e.g. syntax error, disposable domain, missing '@', etc.)."
            )
        }]

# ========== Tool ==========
@function_tool
def validate_emails(emails: List[str]) -> str:
    """
    Validates a list of email addresses and explains invalid ones.
    """
    try:
        prompt = EmailValidationInput(emails=emails).to_prompt()
        result = asyncio.run(Runner.run(email_validator_agent, prompt))
        return result.final_output or "⚠️ No validation result returned."
    except Exception as e:
        return f"❌ Error validating emails: {str(e)}"

# ========== Agent ==========
email_validator_agent = Agent(
    name="EmailValidatorAgent",
    instructions=(
        "You're an expert in email address validation.\n"
        "Your job is to analyze a list of email addresses and determine which are valid.\n\n"
        "✅ Rules:\n"
        "- Check for valid syntax (username@domain).\n"
        "- Warn about disposable or suspicious domains.\n"
        "- Explain the reason if an address is invalid.\n\n"
        "⚠️ If the list is empty or badly formatted, warn the user."
    ),
    tools=[validate_emails],
    model=model
)

# ========== Automation Wrapper ==========
async def run_email_validator_agent(emails: List[str]) -> str:
    """
    Use this in automation pipelines, batch runs, or manual scripts.
    """
    try:
        prompt = EmailValidationInput(emails=emails).to_prompt()
        result = await Runner.run(email_validator_agent, prompt)
        return result.final_output or "⚠️ Validation failed."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== Tool Wrapper ==========
def get_email_validator_tool():
    """
    Expose this agent as a tool — to be used inside orchestrators.
    """
    return email_validator_agent.as_tool(
        tool_name="email_validator_tool",
        tool_description="Validates a list of email addresses and explains if they're invalid."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("📬 Email Validator Agent Ready!")
        while True:
            raw_input = input("🔎 Enter comma-separated emails (or 'exit'): ").strip()
            if raw_input.lower() in ["exit", "quit"]:
                break
            emails = [email.strip() for email in raw_input.split(",") if email.strip()]
            try:
                prompt = EmailValidationInput(emails=emails).to_prompt()
                result = await Runner.run(email_validator_agent, prompt)
                print("✅ Validation Result:\n", result.final_output)
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(main())
