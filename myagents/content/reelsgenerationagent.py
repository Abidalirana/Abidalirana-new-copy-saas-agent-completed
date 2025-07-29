# ✅ Sample Output: `reelsgenerationagent.py`

import os, sys, asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel

# === Path Setup ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# === Environment Setup ===
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

# === Schema ===
class ReelsTopic(BaseModel):
    topic: str

# === Tool ===
@function_tool
def generate_reels_script(topic: str) -> str:
    return f"Create a short, catchy, and viral Instagram reel script for the topic: {topic}"

# === Agent ===
reels_generation_agent = Agent(
    name="ReelsGenerationAgent",
    instructions="""
You're an Instagram Reels script writer.

Your job is to craft short, catchy, and highly shareable video scripts ideal for Instagram Reels.

🎯 Instructions:
- Use 'generate_reels_script' tool.
- Keep it short: under 60 seconds.
- Structure: Hook → Quick Value or Tip → Strong CTA.
- Style should be fun, trendy, and mobile-first.
- Use emojis, slang, trending phrases if relevant.

Audience: Gen Z, content creators, personal brands, marketers.
    """,
    tools=[generate_reels_script],
    model=model
)

# === CLI Runner ===
if __name__ == "__main__":
    async def cli():
        print("📱 Reels Generation Agent Ready!")
        while True:
            topic = input("🎬 Enter a reels topic (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            result = await Runner.run(reels_generation_agent, [{"role": "user", "content": topic}])
            print("\n🔥 Reels Script Output:\n")
            print(result.final_output)

    asyncio.run(cli())

# === Async Automation ===
async def run_reels_generation_agent(topic: str) -> str:
    if not topic:
        topic = "Boost productivity with AI tools"

    result = await Runner.run(reels_generation_agent, [{"role": "user", "content": topic}])
    return result.final_output

# === Export as Tool ===
def get_reels_generation_tool():
    return reels_generation_agent.as_tool(
        tool_name="reels_generation_tool",
        tool_description="Generate viral and catchy Instagram reels scripts from a topic"
    )
