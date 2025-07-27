# ✅ Agent: kpitrackeragent.py

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
class KPIInput(BaseModel):
    topic: str

# ========== Tool ==========
@function_tool
def track_kpis(topic: str) -> dict:
    """
    Simulated KPI tracking logic for a given topic.
    """
    try:
        return {
            "topic": topic,
            "Traffic": "12.4K",
            "Conversion Rate": "3.2%",
            "Bounce Rate": "41%"
        }
    except Exception as e:
        return {"error": str(e)}

# ========== Agent ==========
kpitracker_agent = Agent(
    name="KPITrackerAgent",
    instructions=(
        "You're a KPI analytics expert. Track and summarize the key performance indicators for a given topic. "
        "Always use track_kpis tool first. Fall back to model for context if no data is available."
    ),
    tools=[track_kpis],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📊 KPI Tracker Agent Ready!")
        while True:
            user_input = input("Enter a topic (e.g., AI, Marketing) or 'exit': ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            input_data = [{"role": "user", "content": f"Track KPIs for {user_input}"}]
            result = await Runner.run(kpitracker_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_kpi_tracker_agent(topic: str) -> str:
    if not topic:
        topic = "SEO"  # Default fallback
    input_data = [{"role": "user", "content": f"Track KPIs for {topic}"}]
    try:
        result = await Runner.run(kpitracker_agent, input_data)
        return result.final_output or "⚠️ KPI data not found."
    except Exception as e:
        return f"⚠️ KPI Tracker agent failed: {str(e)}"

# ========== Tool Getter for Orchestrator ==========
def get_kpi_tracker_tool():
    """
    Exposes KPITrackerAgent as a tool for orchestrators.
    """
    return kpitracker_agent.as_tool(
        tool_name="kpi_tracker_agent",
        tool_description="Tracks and summarizes key performance indicators for a given topic."
    )
