# contentqueuemanager_agent.py

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# ========== Config ==========
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

# ========== Simulated In-Memory Queue ==========
QUEUE_DB = [
    {"title": "Post 1", "created": "2024-07-20"},
    {"title": "Post 2", "created": "2024-07-21"},
    {"title": "Post 3", "created": "2024-07-22"},
]

# ========== Schema ==========
class QueueFilterInput(BaseModel):
    query: str | None = None

# ========== Tool ==========
@function_tool
def view_content_queue(data: QueueFilterInput) -> str:
    """
    View content queue. Optionally filter posts by keyword.
    """
    if data.query:
        filtered = [item["title"] for item in QUEUE_DB if data.query.lower() in item["title"].lower()]
        return f"🔍 Found {len(filtered)} items with '{data.query}': {filtered}"
    return f"📅 Queue has {len(QUEUE_DB)} total items."

# ========== Agent ==========
contentqueue_agent = Agent(
    name="ContentQueueManagerAgent",
    instructions=(
        "You're a content queue maintenance agent.\n\n"
        "🛠️ Responsibilities:\n"
        "- Use the tool `view_content_queue` to check the queue.\n"
        "- If user provides a query, filter the queue.\n"
        "- Always return clear, friendly summaries."
    ),
    tools=[view_content_queue],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":
    async def main():
        print("🗃️ Content Queue Agent Ready!")
        while True:
            query = input("🔎 Enter a filter keyword (or press Enter to view all, 'exit' to quit): ").strip()
            if query.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break
            prompt = f"View content queue"
            if query:
                prompt += f" with keyword '{query}'"
            result = await Runner.run(contentqueue_agent, [{"role": "user", "content": prompt}])
            print("\n" + result.final_output)

    asyncio.run(main())

# ========== Automation ==========
async def run_contentqueue_agent(query: str = None) -> str:
    prompt = f"View content queue" + (f" with keyword '{query}'" if query else "")
    result = await Runner.run(contentqueue_agent, [{"role": "user", "content": prompt}])
    return result.final_output

# ========== Tool Export ==========
def get_contentqueue_agent_tool():
    return contentqueue_agent.as_tool(
        tool_name="content_queue_manager",
        tool_description="View or filter content queue items"
    )
