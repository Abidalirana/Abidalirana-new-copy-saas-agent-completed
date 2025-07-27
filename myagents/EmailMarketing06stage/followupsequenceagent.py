import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

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
class FollowUpSequenceInput(BaseModel):
    previous_email: str
    days_since_last_contact: int
    tone: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Write a follow-up email {self.days_since_last_contact} days after the last message.\n"
                f"Maintain a {self.tone} tone.\n"
                f"Previous message:\n{self.previous_email}"
            )
        }]

# ========== Tool ==========
@function_tool
def write_follow_up_email(previous_email: str, days_since_last_contact: int, tone: str) -> str:
    """
    Generates a follow-up email based on a previous message and tone.
    """
    try:
        prompt = FollowUpSequenceInput(
            previous_email=previous_email,
            days_since_last_contact=days_since_last_contact,
            tone=tone
        ).to_prompt()
        result = asyncio.run(Runner.run(follow_up_agent, prompt))
        return result.final_output or "⚠️ No follow-up email generated. Try again."
    except Exception as e:
        return f"❌ Error generating follow-up email: {str(e)}"

# ========== Agent ==========
follow_up_agent = Agent(
    name="FollowUpSequenceAgent",
    instructions=(
        "You're a follow-up email assistant. Your job is to write timely, short, and tone-matched follow-up emails.\n\n"
        "✅ Rules:\n"
        "- Use the number of days to judge urgency.\n"
        "- Be polite but persistent.\n"
        "- Keep the email concise (under 120 words).\n"
        "- Match the requested tone: casual, professional, etc.\n\n"
        "⚠️ If the previous message is unclear or empty, write a basic polite reminder."
    ),
    tools=[write_follow_up_email],
    model=model
)

# ========== Automation Wrapper ==========
async def run_follow_up_agent(previous_email: str, days_since_last_contact: int, tone: str) -> str:
    """
    Use this in automation pipelines, workflows, or internal flows.
    """
    try:
        prompt = FollowUpSequenceInput(
            previous_email=previous_email,
            days_since_last_contact=days_since_last_contact,
            tone=tone
        ).to_prompt()
        result = await Runner.run(follow_up_agent, prompt)
        return result.final_output or "⚠️ No follow-up message returned."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== Tool Wrapper ==========
def get_follow_up_tool():
    """
    Expose this agent as a callable tool inside other orchestrators.
    """
    return follow_up_agent.as_tool(
        tool_name="follow_up_writer",
        tool_description="Generates short, tone-adjusted follow-up emails based on message and delay."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("📨 Follow-Up Email Agent Ready!")
        while True:
            prev = input("✉️ Enter previous email content (or 'exit'): ").strip()
            if prev.lower() in ["exit", "quit"]:
                break
            days = input("📆 Days since last contact: ").strip()
            tone = input("🗣️ Desired tone (e.g. professional, casual): ").strip()
            try:
                prompt = FollowUpSequenceInput(
                    previous_email=prev,
                    days_since_last_contact=int(days),
                    tone=tone
                ).to_prompt()
                result = await Runner.run(follow_up_agent, prompt)
                print("✅ Follow-Up Email:\n", result.final_output)
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(main())
