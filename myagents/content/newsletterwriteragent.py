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
class NewsletterInput(BaseModel):
    idea: str

# ========== Tool ==========
@function_tool
def generate_newsletter_draft(idea: str) -> str:
    """
    Generates a professional long-form newsletter based on a single idea.
    """
    return (
        f"📰 **Newsletter Draft on: {idea.title()}**\n\n"
        f"Hello Readers,\n\n"
        f"Today, we're diving into a crucial topic: **{idea.title()}**.\n\n"
        f"In recent weeks, the landscape around this topic has seen a wave of innovation, "
        f"discussion, and strategic movement from key players in the industry.\n\n"
        f"Here’s a breakdown of what matters most, why you should care, and how it affects the broader ecosystem.\n\n"
        f"🔍 **Key Insight**: The momentum around `{idea}` is shaping how companies build, how investors bet, "
        f"and how users interact with emerging tools.\n\n"
        f"📈 **Trends & Stats**:\n"
        f"- [Insert key stat 1]\n"
        f"- [Insert stat 2]\n"
        f"- [Insert example/company highlighting the topic]\n\n"
        f"🚀 **Action Step**: If you're exploring `{idea}`, now is the time to take a deeper look into how it fits your strategy.\n\n"
        f"Until next time,\n\nYour Friendly Agent."
    )

# ========== Agent ==========
newsletter_agent = Agent(
    name="NewsletterWriterAgent",
    instructions="""
You're a Newsletter Writing Assistant.
Your job is to take a content idea and write a professional long-form newsletter draft based on it.

🧠 Writing Rules:
- Always use the `generate_newsletter_draft` tool.
- Make content clear, well-structured, and valuable to tech/startup/investor readers.
- Keep tone professional but accessible.
- Use markdown headings and bullet lists.

✅ Output should look like a polished newsletter draft ready to publish.
""",
    tools=[generate_newsletter_draft],
    model=model
)

# ========== CLI Mode ==========
if __name__ == "__main__":
    async def main():
        print("📬 Newsletter Writer Agent Ready!")
        while True:
            topic = input("🧠 Enter a content idea (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            input_data = [{"role": "user", "content": f"Write a newsletter on: {topic}"}]
            result = await Runner.run(newsletter_agent, input_data)
            print("\n📢 Newsletter Output:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_newsletter_agent(idea: str) -> str:
    """
    Automation runner for NewsletterWriterAgent.
    Call this from orchestrator: await run_newsletter_agent("web3 for small businesses")
    """
    if not idea:
        idea = "technology"  # Default fallback

    input_data = [{"role": "user", "content": f"Write a newsletter on: {idea}"}]
    result = await Runner.run(newsletter_agent, input_data)
    return result.final_output

# ========== Export as Tool ==========
def get_newsletter_agent_tool():
    """
    Exported NewsletterWriterAgent as a tool for orchestrator or other agents.
    """
    return newsletter_agent.as_tool(
        tool_name="newsletter_writer",
        tool_description="Generate a professional newsletter draft based on an idea"
    )
