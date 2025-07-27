# creativebriefagent.py

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
class CreativeBriefInput(BaseModel):
    product_name: str
    target_audience: str
    key_message: str

    def to_messages(self):
        return [
            {
                "role": "user",
                "content": (
                    f"Create a creative brief for the product '{self.product_name}', "
                    f"targeting '{self.target_audience}', focusing on the key message: '{self.key_message}'."
                )
            }
        ]

# ========== Tools ==========
@function_tool
def generate_creative_brief(product_name: str, target_audience: str, key_message: str) -> str:
    try:
        if not product_name or not target_audience or not key_message:
            raise ValueError("Missing product name, target audience, or key message.")

        return (
            f"🎨 Creative Brief for {product_name}\n"
            f"👥 Target Audience: {target_audience}\n"
            f"💬 Key Message: {key_message}\n\n"
            "📋 Objectives:\n"
            "- Clearly communicate the value proposition.\n"
            "- Engage the audience emotionally.\n"
            "- Drive conversion through a compelling call to action.\n\n"
            "🎯 Tone & Style:\n"
            "- Friendly, confident, and clear.\n"
            "- Visuals should align with brand identity.\n\n"
            "📅 Deliverables:\n"
            "- Ad copy\n"
            "- Visual concepts\n"
            "- Suggested channels and timings."
        )
    except Exception as e:
        return (
            f"⚠️ Error generating creative brief: {str(e)}\n"
            "Fallback: Provide a simple message focusing on product benefits and target audience."
        )

# ========== Agent ==========
creative_brief_agent = Agent(
    name="CreativeBriefAgent",
    instructions=(
        "You are a Creative Brief Generator. Your job is to create a clear and concise creative brief "
        "for marketing campaigns based on product details and audience.\n\n"
        "🧠 Rules:\n"
        "- Focus on key message clarity.\n"
        "- Include objectives, tone, and deliverables.\n"
        "- Keep it concise and actionable.\n\n"
        "✅ Output format:\n"
        "- Product Name\n"
        "- Target Audience\n"
        "- Key Message\n"
        "- Objectives\n"
        "- Tone & Style\n"
        "- Deliverables"
    ),
    tools=[generate_creative_brief],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🎨 Creative Brief Agent Ready!")
        while True:
            product_name = input("📦 Enter Product Name: ").strip()
            target_audience = input("👥 Enter Target Audience: ").strip()
            key_message = input("💡 Enter Key Message: ").strip()

            if any(x.lower() in ["exit", "quit"] for x in [product_name, target_audience, key_message]):
                print("👋 Exiting. Bye!")
                break

            if not product_name or not target_audience or not key_message:
                print("⚠️ Please provide all inputs.\n")
                continue

            input_data = CreativeBriefInput(
                product_name=product_name,
                target_audience=target_audience,
                key_message=key_message
            ).to_messages()

            try:
                result = await Runner.run(creative_brief_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Creative brief generation failed. Fallback: Simple product benefit message. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_creative_brief_agent(product_name: str, target_audience: str, key_message: str) -> str:
    if not product_name or not target_audience or not key_message:
        return "⚠️ Missing required data for creative brief."

    input_data = CreativeBriefInput(
        product_name=product_name,
        target_audience=target_audience,
        key_message=key_message
    ).to_messages()

    try:
        result = await Runner.run(creative_brief_agent, input_data)
        return result.final_output or "⚠️ No output generated. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception occurred: {e}\n"
            "Fallback: Provide simple product benefits and audience description."
        )
#==================
# ========== Tool Export Function ========== #
def get_creative_brief_agent_tool():
    """
    Exposes CreativeBriefAgent as a tool for orchestrators.
    """
    return creative_brief_agent.as_tool(
        tool_name="creative_brief_agent",
        tool_description="Generates a creative brief using product name, target audience, and key message."
    )
