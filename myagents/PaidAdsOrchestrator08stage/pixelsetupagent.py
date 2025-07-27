# pixelSetupAgent.py

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
class PixelSetupInput(BaseModel):
    platform: str
    goal: str

    def to_messages(self):
        return [
            {"role": "user", "content": f"Set up a tracking pixel for {self.platform} with the primary goal of '{self.goal}'. What steps should I follow?"}
        ]

# ========== Tools ==========
@function_tool
def setup_tracking_pixel(platform: str, goal: str) -> str:
    """
    Provide detailed instructions to set up a tracking pixel for the specified platform and conversion goal.
    """
    try:
        if not platform or not goal:
            raise ValueError("Missing platform or goal information.")

        return (
    f"📍 Pixel Setup Guide for {platform}\n"
    f"1️⃣ Go to your {platform} Ads Manager.\n"
    "2️⃣ Navigate to 'Events Manager' > 'Pixels'.\n"
    "3️⃣ Create a new pixel or use existing one.\n"
    f"4️⃣ Set the goal: {goal}.\n"
    "5️⃣ Install the base pixel code on all site pages.\n"
    "6️⃣ Add event code to the goal-conversion page (e.g., thank you page).\n"
    "7️⃣ Use Tag Manager or CMS plugin if available.\n"
    "✅ Done. Test using Pixel Helper or Debug tool."
)

    except Exception as e:
        return (
            f"⚠️ Error setting up pixel: {str(e)}\n"
            "Fallback steps: Use Google Tag Manager to install universal event pixel code across the site, then verify in Ads dashboard."
        )

# ========== Agent ==========
pixel_setup_agent = Agent(
    name="PixelSetupAgent",
    instructions=(
        "You are a Pixel Setup Assistant Agent. Your job is to provide easy-to-follow, accurate steps to install a tracking pixel for a chosen ad platform based on a campaign goal.\n\n"
        "🧠 Setup Rules:\n"
        "- Give the exact steps in simple terms.\n"
        "- Include tools/platforms to verify pixel working.\n"
        "- Handle multiple platforms if needed (Meta, Google, TikTok).\n"
        "- Fallback to Tag Manager if platform-specific flow fails.\n\n"
        "✅ Output Format:\n"
        "- Platform Name\n"
        "- Campaign Goal\n"
        "- Pixel Setup Instructions (Step by step)\n\n"
        "⚠️ Avoid overly technical language. Make it beginner-friendly."
    ),
    tools=[setup_tracking_pixel],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📊 Pixel Setup Agent Ready!")
        while True:
            platform = input("🧱 Enter Ad Platform (Meta, Google, TikTok, etc.): ").strip()
            goal = input("🎯 Enter Campaign Goal (Purchase, Signup, etc.): ").strip()

            if platform.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            if not platform or not goal:
                print("⚠️ Please provide both platform and goal.\n")
                continue

            input_data = PixelSetupInput(platform=platform, goal=goal).to_messages()
            try:
                result = await Runner.run(pixel_setup_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Pixel setup failed. Fallback: Use GTM universal pixel install. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_pixel_setup_agent(platform: str, goal: str) -> str:
    """
    Programmatic runner for PixelSetupAgent – used by orchestrator.
    """
    if not platform or not goal:
        return "⚠️ Missing required data for pixel setup."

    input_data = PixelSetupInput(platform=platform, goal=goal).to_messages()
    try:
        result = await Runner.run(pixel_setup_agent, input_data)
        return result.final_output or "⚠️ No output generated. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception occurred: {e}\n"
            "Fallback: Use Google Tag Manager to install a generic tracking pixel and verify installation manually."
        )
#=================================
# ========== Tool Export Function ========== #
def get_pixel_setup_agent_tool():
    """
    Exposes PixelSetupAgent as a tool for orchestrators.
    """
    return pixel_setup_agent.as_tool(
        tool_name="pixel_setup_agent",
        tool_description="Guides users through setting up ad tracking pixels for platforms like Meta, Google, TikTok."
    )
