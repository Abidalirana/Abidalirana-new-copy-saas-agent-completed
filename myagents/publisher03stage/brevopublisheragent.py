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
class PublishInput(BaseModel):
    title: str
    body: str

# ========== Tool ==========
@function_tool
def publish_to_brevo(data: PublishInput) -> str:
    """
    Simulates publishing content to Brevo (email/newsletter platform).
    """
    return (
        f"✅ Content Published to Brevo!\n\n"
        f"📰 Title: {data.title}\n"
        f"📄 Body: {data.body[:100]}..."  # Truncated preview
    )

# ========== Agent ==========
brevopublisher_agent = Agent(
    name="BrevoPublisherAgent",
    instructions=(
        "You're an email campaign agent responsible for publishing content to Brevo.\n"
        "Use the tool `publish_to_brevo` to simulate sending newsletters.\n\n"
        "Guidelines:\n"
        "- Always publish with clear subject and body.\n"
        "- Ensure body content is informative and properly formatted.\n"
        "- Respond in a helpful, confident manner."
    ),
    tools=[publish_to_brevo],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":
    async def main():
        print("📤 Brevo Publisher Agent Ready!")
        while True:
            title = input("✏️ Enter newsletter title (or 'exit'): ").strip()
            if title.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            body = input("📝 Enter body content: ").strip()
            user_input = [{"role": "user", "content": f"Send newsletter titled '{title}' with body:\n{body}"}]
            result = await Runner.run(brevopublisher_agent, user_input)
            print("\n" + result.final_output)

    asyncio.run(main())

# ========== Automation ==========
async def run_brevo_publisher(title: str, body: str) -> str:
    result = await Runner.run(
        brevopublisher_agent,
        [{"role": "user", "content": f"Send newsletter titled '{title}' with body:\n{body}"}]
    )
    return result.final_output

# ========== Tool Export ==========
def get_brevo_agent_tool():
    return brevopublisher_agent.as_tool(
        tool_name="brevo_publisher",
        tool_description="Publishes newsletter content to Brevo platform"
    )
