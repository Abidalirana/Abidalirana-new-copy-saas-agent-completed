# ✅ Sample Output: `videogenerationagent.py`

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
class VideoTopic(BaseModel):
    topic: str

# === Tool ===
@function_tool
def generate_video_script(topic: str) -> str:
    return f"Create an engaging explainer or promotional video script for the topic: {topic}"

# === Agent ===
video_generation_agent = Agent(
    name="VideoGenerationAgent",
    instructions="""
You're a video script generator.

Your job is to produce short, clear, and visually engaging scripts for explainer or promo videos based on a topic.

🎯 Instructions:
- Use 'generate_video_script' tool.
- Scripts should be 60–90 seconds long.
- Structure: Hook → Problem → Solution → CTA.
- Output should be easy to visualize.
- Write like a YouTube script — conversational & clear.

Audience: startups, marketers, product designers.
    """,
    tools=[generate_video_script],
    model=model
)

# === CLI Runner ===
if __name__ == "__main__":
    async def cli():
        print("🎬 Video Generation Agent Ready!")
        while True:
            topic = input("🎥 Enter a video topic (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            result = await Runner.run(video_generation_agent, [{"role": "user", "content": topic}])
            print("\n📹 Video Script Output:\n")
            print(result.final_output)

    asyncio.run(cli())

# === Async Automation ===
async def run_video_generation_agent(topic: str) -> str:
    if not topic:
        topic = "How AI transforms marketing"

    result = await Runner.run(video_generation_agent, [{"role": "user", "content": topic}])
    return result.final_output

# === Export as Tool ===
def get_video_generation_tool():
    return video_generation_agent.as_tool(
        tool_name="video_generation_tool",
        tool_description="Generate a promotional or explainer video script from topic"
    )
