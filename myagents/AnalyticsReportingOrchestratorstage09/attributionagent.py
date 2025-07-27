# ✅ Agent: attributionagent.py

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
class AttributionInput(BaseModel):
    campaign_id: str

    def to_messages(self):
        return [{"role": "user", "content": f"Get attribution for campaign {self.campaign_id}"}]

# ========== Tool ==========
@function_tool
def calculate_attribution(campaign_id: str) -> dict:
    """
    Simulated attribution logic for a campaign.
    """
    try:
        return {
            "CAMP123": {"source": "Google Ads", "revenue": "$13,200", "roi": "240%"},
            "CAMP456": {"source": "Facebook Ads", "revenue": "$9,500", "roi": "180%"}
        }.get(campaign_id, {})
    except Exception as e:
        return {"error": str(e)}

# ========== Agent ==========
attribution_agent = Agent(
    name="AttributionAgent",
    instructions=(
        "You're a marketing attribution expert. Your job is to attribute revenue to correct sources.\n"
        "Always use calculate_attribution. Fallback to LLM with explanation if data is missing."
    ),
    tools=[calculate_attribution],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📈 Attribution Agent Ready!")
        while True:
            user_input = input("Enter campaign ID (e.g., CAMP123) or 'exit': ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            input_data = AttributionInput(campaign_id=user_input).to_messages()
            result = await Runner.run(attribution_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_attribution_agent(campaign_id: str) -> str:
    if not campaign_id:
        campaign_id = "CAMP123"  # Default fallback
    input_data = AttributionInput(campaign_id=campaign_id).to_messages()
    try:
        result = await Runner.run(attribution_agent, input_data)
        return result.final_output or "⚠️ Attribution data not found."
    except Exception as e:
        return f"⚠️ Attribution agent failed: {str(e)}"

# ========== Tool Export Function ==========
def get_attribution_agent_tool():
    """
    Exposes AttributionAgent as a tool for orchestrators.
    """
    return attribution_agent.as_tool(
        tool_name="attribution_agent",
        tool_description="Analyzes marketing attribution data for a given campaign ID."
    )
