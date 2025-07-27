# audiencetargetingagent.py

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
class AudienceTargetingInput(BaseModel):
    product_category: str
    marketing_goal: str

    def to_messages(self):
        return [
            {
                "role": "user",
                "content": (
                    f"Suggest ideal audience targeting parameters for a {self.product_category} product "
                    f"with the marketing goal: {self.marketing_goal}."
                )
            }
        ]

# ========== Tools ==========
@function_tool
def suggest_audience_targeting(product_category: str, marketing_goal: str) -> str:
    try:
        if not product_category or not marketing_goal:
            raise ValueError("Missing product category or marketing goal.")

        return (
            f"🎯 Audience Targeting Suggestions for {product_category}\n"
            f"Goal: {marketing_goal}\n\n"
            "👥 Demographics:\n"
            "- Age: 25-45\n"
            "- Gender: All\n"
            "- Location: Urban areas with high purchasing power\n\n"
            "💻 Interests:\n"
            "- Related to technology, lifestyle, and trends\n\n"
            "📱 Behaviors:\n"
            "- Online shoppers\n"
            "- Engaged with similar products\n\n"
            "🕒 Best time to target:\n"
            "- Evenings and weekends"
        )
    except Exception as e:
        return (
            f"⚠️ Error generating audience targeting: {str(e)}\n"
            "Fallback: Use broad targeting on major platforms and refine over time."
        )

# ========== Agent ==========
audience_targeting_agent = Agent(
    name="AudienceTargetingAgent",
    instructions=(
        "You are an Audience Targeting Assistant. Your job is to suggest ideal audience parameters "
        "based on product category and marketing goals.\n\n"
        "🧠 Rules:\n"
        "- Provide demographic, interest, and behavioral segments.\n"
        "- Include timing suggestions.\n"
        "- Keep suggestions actionable and realistic.\n\n"
        "✅ Output format:\n"
        "- Demographics\n"
        "- Interests\n"
        "- Behaviors\n"
        "- Timing\n"
    ),
    tools=[suggest_audience_targeting],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🎯 Audience Targeting Agent Ready!")
        while True:
            product_category = input("📦 Enter Product Category: ").strip()
            marketing_goal = input("🎯 Enter Marketing Goal: ").strip()

            if any(x.lower() in ["exit", "quit"] for x in [product_category, marketing_goal]):
                print("👋 Exiting. Bye!")
                break

            if not product_category or not marketing_goal:
                print("⚠️ Please provide all inputs.\n")
                continue

            input_data = AudienceTargetingInput(
                product_category=product_category,
                marketing_goal=marketing_goal
            ).to_messages()

            try:
                result = await Runner.run(audience_targeting_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Audience targeting failed. Fallback: Use broad targeting initially. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_audience_targeting_agent(product_category: str, marketing_goal: str) -> str:
    if not product_category or not marketing_goal:
        return "⚠️ Missing required data for audience targeting."

    input_data = AudienceTargetingInput(
        product_category=product_category,
        marketing_goal=marketing_goal
    ).to_messages()

    try:
        result = await Runner.run(audience_targeting_agent, input_data)
        return result.final_output or "⚠️ No output generated. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception occurred: {e}\n"
            "Fallback: Use broad targeting on platforms and optimize after data collection."
        )
#=============================
# ========== Tool Export Function ========== #
def get_audience_targeting_agent_tool():
    """
    Exposes AudienceTargetingAgent as a tool for orchestrators.
    """
    return audience_targeting_agent.as_tool(
        tool_name="audience_targeting_agent",
        tool_description="Suggests ideal audience targeting parameters based on product category and marketing goals."
    )
