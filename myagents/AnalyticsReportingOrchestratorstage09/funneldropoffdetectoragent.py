# ✅ Agent: funneldropoffdetectoragent.py

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
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
class FunnelInput(BaseModel):
    funnel_stage: str

# ========== Tool ==========
@function_tool
def detect_funnel_dropoff(funnel_stage: str) -> dict:
    """
    Simulated funnel drop-off detection.
    """
    try:
        return {
            "Awareness": {"dropoff_rate": "15%", "reason": "Low engagement"},
            "Consideration": {"dropoff_rate": "25%", "reason": "Pricing concerns"},
            "Conversion": {"dropoff_rate": "35%", "reason": "Checkout friction"}
        }.get(funnel_stage, {})
    except Exception as e:
        return {"error": str(e)}

# ========== Agent ==========
funnel_dropoff_agent = Agent(
    name="FunnelDropoffDetectorAgent",
    instructions=(
        "You're a funnel drop-off detection specialist.\n"
        "Always use detect_funnel_dropoff. If missing, predict using reasoning."
    ),
    tools=[detect_funnel_dropoff],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🧩 Funnel Drop-off Detector Ready!")
        while True:
            user_input = input("Enter funnel stage (e.g., Awareness) or 'exit': ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            input_data = [{"role": "user", "content": f"Detect drop-off in {user_input} stage"}]
            result = await Runner.run(funnel_dropoff_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_funnel_dropoff_agent(funnel_stage: str) -> str:
    if not funnel_stage:
        funnel_stage = "Awareness"
    input_data = [{"role": "user", "content": f"Detect drop-off in {funnel_stage} stage"}]
    try:
        result = await Runner.run(funnel_dropoff_agent, input_data)
        return result.final_output or "⚠️ No drop-off data found."
    except Exception as e:
        return f"⚠️ Funnel Drop-off Agent failed: {str(e)}"

# ========== Tool Wrapper ==========
def get_funnel_dropoff_detector_tool():
    """
    Exposes FunnelDropoffDetectorAgent as a tool for orchestrators.
    """
    return funnel_dropoff_agent.as_tool(
        tool_name="funnel_dropoff_detector_agent",
        tool_description="Detects drop-off rates and reasons in specific funnel stages (e.g., Awareness, Consideration, Conversion)."
    )
