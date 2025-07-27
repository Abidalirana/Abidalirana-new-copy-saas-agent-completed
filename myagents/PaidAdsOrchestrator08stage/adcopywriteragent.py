# adcopywriteragent.py

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
class AdCopyInput(BaseModel):
    product_name: str
    target_audience: str
    campaign_goal: str

    def to_messages(self):
        return [
            {
                "role": "user",
                "content": (
                    f"Write a persuasive ad copy for the product '{self.product_name}' targeting '{self.target_audience}' "
                    f"with the goal: '{self.campaign_goal}'. Make it punchy and conversion-focused."
                )
            }
        ]

# ========== Tools ==========
@function_tool
def write_ad_copy(product_name: str, target_audience: str, campaign_goal: str) -> str:
    """
    Generate compelling ad copy tailored to the product, audience, and goal.
    """
    try:
        if not product_name or not target_audience or not campaign_goal:
            raise ValueError("Missing required input data for ad copy.")

        return (
            f"📝 Ad Copy for {product_name}\n"
            f"Targeting: {target_audience}\n"
            f"Goal: {campaign_goal}\n\n"
            f"🔥 \"Introducing {product_name} – the game-changer your life needs! Designed especially for {target_audience}, "
            f"this is your chance to {campaign_goal.lower()} like never before. Don't miss out – act now and experience the difference!\"\n"
            "✅ CTA: Shop Now | Learn More | Sign Up Today"
        )

    except Exception as e:
        return (
            f"⚠️ Error generating ad copy: {str(e)}\n"
            "Fallback: Use a standard benefits-driven headline followed by a clear call-to-action (CTA)."
        )

# ========== Agent ==========
ad_copy_agent = Agent(
    name="AdCopywriterAgent",
    instructions=(
        "You are an Ad Copywriter Agent. Your job is to generate punchy, persuasive ad copy based on the product, target audience, and campaign goal.\n\n"
        "🧠 Copywriting Rules:\n"
        "- Use clear, conversion-optimized language.\n"
        "- Emphasize value and benefits.\n"
        "- Include a strong CTA.\n\n"
        "✅ Output Format:\n"
        "- Headline or opening hook\n"
        "- Body (1-2 persuasive lines)\n"
        "- CTA\n\n"
        "⚠️ Make it emotionally engaging and tailored to the audience."
    ),
    tools=[write_ad_copy],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📝 Ad Copywriter Agent Ready!")
        while True:
            product_name = input("📦 Enter Product Name: ").strip()
            target_audience = input("👥 Enter Target Audience: ").strip()
            campaign_goal = input("🎯 Enter Campaign Goal: ").strip()

            if any(x.lower() in ["exit", "quit"] for x in [product_name, target_audience, campaign_goal]):
                print("👋 Exiting. Bye!")
                break

            if not product_name or not target_audience or not campaign_goal:
                print("⚠️ Please provide all inputs.\n")
                continue

            input_data = AdCopyInput(
                product_name=product_name,
                target_audience=target_audience,
                campaign_goal=campaign_goal
            ).to_messages()

            try:
                result = await Runner.run(ad_copy_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Ad copy generation failed. Fallback to a basic headline-CTA format. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_ad_copy_agent(product_name: str, target_audience: str, campaign_goal: str) -> str:
    """
    Programmatic runner for AdCopywriterAgent – used by orchestrator.
    """
    if not product_name or not target_audience or not campaign_goal:
        return "⚠️ Missing required data for ad copy."

    input_data = AdCopyInput(
        product_name=product_name,
        target_audience=target_audience,
        campaign_goal=campaign_goal
    ).to_messages()

    try:
        result = await Runner.run(ad_copy_agent, input_data)
        return result.final_output or "⚠️ No output generated. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception occurred: {e}\n"
            "Fallback: Use a simple message with benefit-driven headline and call to action."
        )
#======================================
# ========== Tool Export Function ========== #
def get_ad_copywriter_agent_tool():
    """
    Exposes AdCopywriterAgent as a tool for orchestrators.
    """
    return ad_copy_agent.as_tool(
        tool_name="ad_copywriter_agent",
        tool_description="Generates persuasive ad copy based on product, target audience, and campaign goal."
    )
