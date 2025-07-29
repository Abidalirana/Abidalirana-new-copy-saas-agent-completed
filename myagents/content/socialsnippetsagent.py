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
class SnippetInput(BaseModel):
    idea: str

# ========== Tool ==========
@function_tool
def generate_social_snippets(idea: str) -> str:
    """
    Creates 3–5 short, engaging LinkedIn/X-style snippets from a content idea.
    """
    return (
        f"📢 Here are 5 social snippets for: **{idea.title()}**\n\n"
        f"1. 🚀 {idea} — Here's why it matters in 2025! #TechTrends #Leadership\n"
        f"2. 💭 Ever wondered how {idea} will reshape the future? It's already happening. #FutureOfWork\n"
        f"3. 📊 Data shows {idea} is transforming industries fast. Are you keeping up? #Innovation\n"
        f"4. 🔍 {idea} isn't just buzz — it's a shift in mindset. Adapt early. #MindsetMatters\n"
        f"5. 🧠 Smart teams are exploring {idea} to unlock efficiency. Are you one of them? #GrowthHacking"
    )

# ========== Agent ==========
social_snippets_agent = Agent(
    name="SocialSnippetsAgent",
    instructions="""
You're a Social Snippets Assistant.
Your job is to turn a single idea into 3–5 engaging LinkedIn/X-style posts.

🧠 Writing Rules:
- Always use the `generate_social_snippets` tool.
- Make each snippet short, punchy, and attention-grabbing.
- Focus on making the content social-media-ready.
- Use emojis, line breaks, hashtags.

✅ Output should look like a post-ready batch of short-form content.
""",
    tools=[generate_social_snippets],
    model=model
)

# ========== Manual CLI Mode ==========
if __name__ == "__main__":
    async def main():
        print("📱 Social Snippets Agent Ready!")
        while True:
            idea = input("🧠 Enter a content idea (or 'exit'): ").strip()
            if idea.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            input_data = [{"role": "user", "content": f"Write social snippets on: {idea}"}]
            result = await Runner.run(social_snippets_agent, input_data)
            print("\n📢 Snippet Output:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_social_snippets_agent(idea: str) -> str:
    """
    Automation runner for SocialSnippetsAgent.
    Call this from orchestrator: await run_social_snippets_agent("future of AI in business")
    """
    if not idea:
        idea = "technology"  # Default fallback

    input_data = [{"role": "user", "content": f"Write social snippets on: {idea}"}]
    result = await Runner.run(social_snippets_agent, input_data)
    return result.final_output

# ========== Export as Tool ==========
def get_social_snippets_agent_tool():
    """
    Exported SocialSnippetsAgent as a tool for orchestrator or other agents.
    """
    return social_snippets_agent.as_tool(
        tool_name="social_snippets_writer",
        tool_description="Generate 3–5 LinkedIn/X-style snippets from a single content idea"
    )
