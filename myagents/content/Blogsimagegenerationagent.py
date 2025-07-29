# ✅ BlogsImageGenerationAgent.py

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
class BlogImagePrompt(BaseModel):
    blog_topic: str

# === Tool ===
#image_tool = ImageGenerationTool()
image_tool = ImageGenerationTool(tool_config={})


@function_tool
def describe_blog_image(blog_topic: str) -> str:
    return f"Create a high-quality blog cover image based on this topic: {blog_topic}. It should be visually engaging and relevant to the blog content."

# === Agent ===
blog_image_generation_agent = Agent(
    name="BlogImageGenerationAgent",
    instructions="""
You are a blog image generation assistant.

🎯 Objective:
- Generate high-quality images for blog posts based on a topic.
- Use 'describe_blog_image' to form a strong visual concept.
- Use 'ImageGenerationTool' to generate the final image.

Target Audience:
- Bloggers
- Content creators
- SEO professionals
- Digital marketers
""",
    tools=[describe_blog_image, image_tool],
    model=model
)

# === CLI Runner ===
if __name__ == "__main__":
    async def cli():
        print("📝 Blog Image Generation Agent Ready!")
        while True:
            topic = input("🖼️ Enter a blog topic (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            result = await Runner.run(blog_image_generation_agent, [{"role": "user", "content": topic}])
            print("\n📸 Generated Blog Image Prompt:\n")
            print(result.final_output)

    asyncio.run(cli())

# === Async Automation ===
async def run_blog_image_generation_agent(blog_topic: str) -> str:
    if not blog_topic:
        blog_topic = "Top 10 Productivity Hacks for Remote Workers"

    result = await Runner.run(blog_image_generation_agent, [{"role": "user", "content": blog_topic}])
    return result.final_output

# === Export as Tool ===
def get_blog_image_generation_tool():
    return blog_image_generation_agent.as_tool(
        tool_name="blog_image_generation_tool",
        tool_description="Generate high-quality, engaging blog images based on blog topics"
    )
