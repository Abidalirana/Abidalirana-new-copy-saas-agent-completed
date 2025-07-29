# ✅ Sample Output: `imagegenerationagent.py`

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
class ImagePrompt(BaseModel):
    prompt: str

# === Tool ===
#image_tool = ImageGenerationTool()
image_tool = ImageGenerationTool(tool_config={})

@function_tool
def describe_image_prompt(prompt: str) -> str:
    return f"Generate a visually appealing image based on this description: {prompt}"

# === Agent ===
image_generation_agent = Agent(
    name="ImageGenerationAgent",
    instructions="""
You're a creative image generation assistant.

Your job is to generate visually stunning, AI-generated images based on user prompts.

🎯 Instructions:
- Use 'describe_image_prompt' for generating caption/visual themes.
- Use 'ImageGenerationTool' to produce images.
- Output should be imaginative, visually rich, and relevant to the topic.

Audience: marketers, social media creators, designers, developers.
""",
    tools=[describe_image_prompt, image_tool],
    model=model
)

# === CLI Runner ===
if __name__ == "__main__":
    async def cli():
        print("🖼️ Image Generation Agent Ready!")
        while True:
            prompt = input("🎨 Enter an image prompt (or 'exit'): ").strip()
            if prompt.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            result = await Runner.run(image_generation_agent, [{"role": "user", "content": prompt}])
            print("\n🧠 Image Description Output:\n")
            print(result.final_output)

    asyncio.run(cli())

# === Async Automation ===
async def run_image_generation_agent(prompt: str) -> str:
    if not prompt:
        prompt = "A futuristic city skyline at sunset in cyberpunk style"

    result = await Runner.run(image_generation_agent, [{"role": "user", "content": prompt}])
    return result.final_output

# === Export as Tool ===
def get_image_generation_tool():
    return image_generation_agent.as_tool(
        tool_name="image_generation_tool",
        tool_description="Generate creative and beautiful images from prompts"
    )
