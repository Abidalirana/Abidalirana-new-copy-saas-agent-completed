# ABTesterAgent.py

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
class ABTestInput(BaseModel):
    campaign_name: str
    variant_a: str
    variant_b: str
    metric: str

    def to_messages(self):
        return [
            {"role": "user", "content": (
                f"Design an A/B test for the campaign '{self.campaign_name}'. "
                f"Variant A: '{self.variant_a}', Variant B: '{self.variant_b}'. "
                f"Focus on improving '{self.metric}'. Provide test setup and success criteria."
            )}
        ]

# ========== Tools ==========
@function_tool
def design_ab_test(campaign_name: str, variant_a: str, variant_b: str, metric: str) -> str:
    """
    Suggest an A/B testing plan with variants and metrics.
    """
    try:
        if not campaign_name or not variant_a or not variant_b or not metric:
            raise ValueError("Missing one or more A/B test components.")

        return (
            f"🧪 A/B Test Plan for '{campaign_name}'\n"
            f"Variant A: {variant_a}\n"
            f"Variant B: {variant_b}\n"
            f"Primary Metric: {metric}\n"
            "Setup:\n"
            "1️⃣ Split audience evenly between Variant A and B.\n"
            "2️⃣ Run test for at least 2 weeks or until statistical significance.\n"
            "3️⃣ Monitor the primary metric daily.\n"
            "Success Criteria:\n"
            "✅ Variant with better improvement in the metric wins.\n"
            "✅ Deploy winning variant for full campaign."
        )
    except Exception as e:
        return (
            f"⚠️ Error designing A/B test: {str(e)}\n"
            "Fallback plan: Run a simple split test with different headlines and measure click-through rate."
        )

# ========== Agent ==========
ab_tester_agent = Agent(
    name="ABTesterAgent",
    instructions=(
        "You are an A/B Testing Specialist. Your job is to create detailed A/B test plans "
        "for digital ad campaigns based on provided variants and a success metric.\n\n"
        "🧠 Testing Rules:\n"
        "- Ensure clear definition of variants.\n"
        "- Include setup steps and duration.\n"
        "- Specify how to measure success.\n"
        "- Provide fallback suggestions for incomplete inputs.\n\n"
        "✅ Output Format:\n"
        "- Campaign Name\n"
        "- Variant A Description\n"
        "- Variant B Description\n"
        "- Primary Metric\n"
        "- Testing Steps\n"
        "- Success Criteria\n\n"
        "⚠️ Be concise, practical, and avoid jargon."
    ),
    tools=[design_ab_test],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🧪 A/B Tester Agent Ready!")
        while True:
            campaign_name = input("📢 Enter Campaign Name: ").strip()
            variant_a = input("🅰️ Describe Variant A: ").strip()
            variant_b = input("🅱️ Describe Variant B: ").strip()
            metric = input("📊 Primary Metric to Improve (e.g., CTR, Conversion Rate): ").strip()

            if campaign_name.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            if not campaign_name or not variant_a or not variant_b or not metric:
                print("⚠️ Please enter all fields.\n")
                continue

            input_data = ABTestInput(
                campaign_name=campaign_name,
                variant_a=variant_a,
                variant_b=variant_b,
                metric=metric
            ).to_messages()
            try:
                result = await Runner.run(ab_tester_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ A/B test generation failed. Fallback:\nRun a headline split test focusing on CTR. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_ab_tester_agent(campaign_name: str, variant_a: str, variant_b: str, metric: str) -> str:
    """
    Programmatic runner for ABTesterAgent – used by orchestrator.
    """
    if not campaign_name or not variant_a or not variant_b or not metric:
        return "⚠️ Missing required inputs for A/B test generation."

    input_data = ABTestInput(
        campaign_name=campaign_name,
        variant_a=variant_a,
        variant_b=variant_b,
        metric=metric
    ).to_messages()
    try:
        result = await Runner.run(ab_tester_agent, input_data)
        return result.final_output or "⚠️ No output from model. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception: {e}\n"
            "Fallback: Run a simple split test on headlines measuring CTR."
        )

#=============================================
# ========== Tool Export Function ========== #
def get_abtester_agent_tool():
    """
    Exposes ABTesterAgent as a tool for orchestrators.
    """
    return ab_tester_agent.as_tool(
        tool_name="ab_tester_agent",
        tool_description="Designs and suggests an A/B testing plan based on two ad variants and a metric."
    )

