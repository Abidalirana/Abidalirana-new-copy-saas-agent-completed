# ✅ Final Output: socialmediaimagegenerationagent.py

import os, sys, asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from agents import Agent, Runner, function_tool, set_tracing_disabled, OpenAIChatCompletionsModel, ImageGenerationTool

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
class SocialPostTopic(BaseModel):
    topic: str

# === Tools ===
@function_tool
def generate_social_post(topic: str) -> str:
    return f"Generate a carousel, quote, or image-based social media post around this topic: {topic}"

#image_tool = ImageGenerationTool()
image_tool = ImageGenerationTool(tool_config={})

# === Agent ===
social_media_image_agent = Agent(
    name="SocialMediaImageAgent",
    instructions="""
You're a social media visual content generator.

Your job is to create caption ideas and generate visually engaging content (like quotes, carousels, and creative graphics) based on a topic.

🎯 Instructions:
- Use 'generate_social_post' for caption/quote generation.
- Use 'ImageGenerationTool' to generate a matching visual.
- Be brief, catchy, and on-trend with modern social media aesthetics.

Audience: social media managers, marketers, influencers, and creators.
""",
    tools=[generate_social_post, image_tool],
    model=model
)

# === CLI Runner ===
if __name__ == "__main__":
    async def cli():
        print("📱 Social Media Image Agent Ready!")
        while True:
            topic = input("🧠 Enter a social media topic (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            result = await Runner.run(social_media_image_agent, [{"role": "user", "content": topic}])
            print("\n📸 Social Media Post Output:\n")
            print(result.final_output)

    asyncio.run(cli())

# === Async Automation ===
async def run_social_media_image_agent(topic: str) -> str:
    if not topic:
        topic = "Motivational quotes for startup founders"

    result = await Runner.run(social_media_image_agent, [{"role": "user", "content": topic}])
    return result.final_output

# === Export as Tool ===
def get_social_media_image_tool():
    return social_media_image_agent.as_tool(
        tool_name="social_media_image_tool",
        tool_description="Generate carousel, quote, or graphic-based social media content from a topic"
    )
