# PerformanceOptimizerAgent.py

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
class PerformanceOptimizerInput(BaseModel):
    campaign_name: str
    current_ctr: float
    current_roas: float

    def to_messages(self):
        return [
            {"role": "user", "content": (
                f"Optimize the performance of campaign '{self.campaign_name}'. "
                f"Current CTR is {self.current_ctr}%, and current ROAS is {self.current_roas}. "
                "Provide actionable recommendations to improve these metrics."
            )}
        ]

# ========== Tools ==========
@function_tool
def optimize_performance(campaign_name: str, current_ctr: float, current_roas: float) -> str:
    """
    Provide performance optimization suggestions for ad campaigns.
    """
    try:
        if not campaign_name or current_ctr is None or current_roas is None:
            raise ValueError("Missing one or more inputs for optimization.")

        recommendations = [
            "Review and improve ad creatives for clarity and emotional appeal.",
            "Test new audience segments to find higher engagement groups.",
            "Adjust bidding strategies for cost efficiency.",
            "Refine ad copy with stronger calls to action.",
            "Increase frequency capping to avoid ad fatigue.",
            "Utilize retargeting campaigns for warm audiences.",
            "Analyze peak engagement times and schedule ads accordingly."
        ]

        return (
            f"🚀 Optimization Plan for Campaign: {campaign_name}\n"
            f"Current CTR: {current_ctr}% | Current ROAS: {current_roas}\n\n"
            "Recommended Actions:\n" +
            "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
        )
    except Exception as e:
        return (
            f"⚠️ Error optimizing performance: {str(e)}\n"
            "Fallback: Focus on improving ad copy and testing new audiences."
        )

# ========== Agent ==========
performance_optimizer_agent = Agent(
    name="PerformanceOptimizerAgent",
    instructions=(
        "You are a Performance Optimization Specialist. Your job is to analyze campaign performance metrics "
        "and provide clear, actionable recommendations to improve CTR and ROAS.\n\n"
        "🧠 Optimization Rules:\n"
        "- Use current CTR and ROAS as baseline.\n"
        "- Suggest practical, prioritized improvements.\n"
        "- Handle missing or incomplete data gracefully.\n\n"
        "✅ Output Format:\n"
        "- Campaign Name\n"
        "- Current Metrics (CTR, ROAS)\n"
        "- List of Recommendations\n\n"
        "⚠️ Keep language simple and actionable."
    ),
    tools=[optimize_performance],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🚀 Performance Optimizer Agent Ready!")
        while True:
            campaign_name = input("📢 Enter Campaign Name: ").strip()
            try:
                current_ctr = float(input("📈 Current CTR (%): ").strip())
                current_roas = float(input("💰 Current ROAS: ").strip())
            except ValueError:
                print("⚠️ Please enter valid numeric values for CTR and ROAS.\n")
                continue

            if campaign_name.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            if not campaign_name:
                print("⚠️ Campaign name is required.\n")
                continue

            input_data = PerformanceOptimizerInput(
                campaign_name=campaign_name,
                current_ctr=current_ctr,
                current_roas=current_roas
            ).to_messages()
            try:
                result = await Runner.run(performance_optimizer_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Performance optimization failed. Fallback:\nFocus on ad creative and audience targeting improvements. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_performance_optimizer_agent(campaign_name: str, current_ctr: float, current_roas: float) -> str:
    """
    Programmatic runner for PerformanceOptimizerAgent – used by orchestrator.
    """
    if not campaign_name or current_ctr is None or current_roas is None:
        return "⚠️ Missing required inputs for performance optimization."

    input_data = PerformanceOptimizerInput(
        campaign_name=campaign_name,
        current_ctr=current_ctr,
        current_roas=current_roas
    ).to_messages()
    try:
        result = await Runner.run(performance_optimizer_agent, input_data)
        return result.final_output or "⚠️ No output from model. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception: {e}\n"
            "Fallback: Improve ad copy and test new audience segments."
        )
#===========================
# ========== Tool Export Function ========== #
def get_performance_optimizer_agent_tool():
    """
    Exposes PerformanceOptimizerAgent as a tool for orchestrators.
    """
    return performance_optimizer_agent.as_tool(
        tool_name="performance_optimizer_agent",
        tool_description="Provides actionable optimization tips for ad campaigns based on CTR and ROAS."
    )
