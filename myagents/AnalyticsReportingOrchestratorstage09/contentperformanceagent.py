# ✅ Agent: contentperformanceagent.py

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
class ContentPerformanceInput(BaseModel):
    content_id: str

# ========== Tool ==========
@function_tool
def analyze_content_performance(content_id: str) -> dict:
    """
    Simulated content performance analysis.
    """
    try:
        return {
            "CONT001": {"views": 4200, "likes": 380, "shares": 120, "CTR": "8.5%"},
            "CONT002": {"views": 2100, "likes": 150, "shares": 70, "CTR": "5.3%"}
        }.get(content_id, {})
    except Exception as e:
        return {"error": str(e)}

# ========== Agent ==========
content_performance_agent = Agent(
    name="ContentPerformanceAgent",
    instructions=(
        "You are a content performance analyzer.\n"
        "Always use analyze_content_performance. If unavailable, reason with the LLM."
    ),
    tools=[analyze_content_performance],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📊 Content Performance Agent Ready!")
        while True:
            user_input = input("Enter content ID (e.g., CONT001) or 'exit': ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            input_data = [{"role": "user", "content": f"Analyze performance for {user_input}"}]
            result = await Runner.run(content_performance_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_content_performance_agent(content_id: str) -> str:
    if not content_id:
        content_id = "CONT001"
    input_data = [{"role": "user", "content": f"Analyze performance for {content_id}"}]
    try:
        result = await Runner.run(content_performance_agent, input_data)
        return result.final_output or "⚠️ No performance data found."
    except Exception as e:
        return f"⚠️ Content Performance Agent failed: {str(e)}"

# ========== Tool Wrapper Function ==========
def get_content_performance_tool():
    """
    Exposes ContentPerformanceAgent as a tool for orchestrators.
    """
    return content_performance_agent.as_tool(
        tool_name="content_performance_agent",
        tool_description="Analyzes how a specific piece of content has performed across key metrics like views, likes, and CTR."
    )
