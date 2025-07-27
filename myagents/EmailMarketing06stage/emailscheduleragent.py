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
class ScheduleEmailInput(BaseModel):
    platform: str  # Lemlist or Brevo
    campaign_name: str
    recipient_email: str
    subject: str
    body: str
    send_time: str  # ISO timestamp or 'now'

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Schedule an email using the following details:\n"
                f"Platform: {self.platform}\n"
                f"Campaign: {self.campaign_name}\n"
                f"Recipient: {self.recipient_email}\n"
                f"Subject: {self.subject}\n"
                f"Body: {self.body}\n"
                f"Send Time: {self.send_time}\n\n"
                "Determine how to schedule this email (via Lemlist or Brevo) and confirm scheduling instructions."
            )
        }]

# ========== Tool ==========
@function_tool
def schedule_email(platform: str, campaign_name: str, recipient_email: str, subject: str, body: str, send_time: str) -> str:
    """
    Schedules an email campaign using Lemlist or Brevo.
    """
    try:
        prompt = ScheduleEmailInput(
            platform=platform,
            campaign_name=campaign_name,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            send_time=send_time
        ).to_prompt()

        result = asyncio.run(Runner.run(email_scheduler_agent, prompt))
        return result.final_output or "⚠️ No scheduling output returned."
    except Exception as e:
        return f"❌ Error scheduling email: {str(e)}"

# ========== Agent ==========
email_scheduler_agent = Agent(
    name="EmailSchedulerAgent",
    instructions=(
        "You're an email campaign scheduler.\n"
        "Your job is to decide how and when to send an email via Lemlist or Brevo.\n\n"
        "✅ Rules:\n"
        "- If send_time is 'now', assume immediate dispatch.\n"
        "- Format time ISO8601 if needed.\n"
        "- Mention the platform and confirm the campaign name.\n"
        "- Validate subject and body length if required.\n\n"
        "⚠️ If platform is not Lemlist or Brevo, or if input is malformed, warn the user."
    ),
    tools=[schedule_email],
    model=model
)

# ========== Automation Entry ==========
async def run_email_scheduler_agent(platform: str, campaign_name: str, recipient_email: str, subject: str, body: str, send_time: str) -> str:
    try:
        prompt = ScheduleEmailInput(
            platform=platform,
            campaign_name=campaign_name,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            send_time=send_time
        ).to_prompt()
        result = await Runner.run(email_scheduler_agent, prompt)
        return result.final_output or "⚠️ Scheduling failed."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== Tool Export ==========
def get_email_scheduler_tool():
    return email_scheduler_agent.as_tool(
        tool_name="email_scheduler",
        tool_description="Schedules an email campaign using Lemlist or Brevo based on user input like time, subject, and platform."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("⏰ Email Scheduler Agent Ready!")
        while True:
            platform = input("📤 Platform (Lemlist or Brevo or 'exit'): ").strip()
            if platform.lower() in ["exit", "quit"]:
                break
            campaign = input("📛 Campaign name: ").strip()
            email = input("📧 Recipient email: ").strip()
            subject = input("✉️ Email subject: ").strip()
            body = input("📝 Email body: ").strip()
            time = input("🕓 Send time (ISO format or 'now'): ").strip()

            try:
                prompt = ScheduleEmailInput(
                    platform=platform,
                    campaign_name=campaign,
                    recipient_email=email,
                    subject=subject,
                    body=body,
                    send_time=time
                ).to_prompt()
                result = await Runner.run(email_scheduler_agent, prompt)
                print("✅ Scheduling Result:\n", result.final_output)
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(main())
