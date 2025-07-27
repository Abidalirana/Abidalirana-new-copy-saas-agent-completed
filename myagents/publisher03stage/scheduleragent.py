import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel

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
class ScheduledPost(BaseModel):
    platform: str
    content: str
    scheduled_time: Optional[str] = None

# ========== Tool ==========
@function_tool
def schedule_posts(posts: List[ScheduledPost]) -> str:
    """
    Schedule posts across platforms like LinkedIn, WordPress, Brevo.
    """
    result = []
    for post in posts:
        if not post.scheduled_time:
            post.scheduled_time = (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        result.append(f"⏰ {post.platform.upper()} scheduled at {post.scheduled_time}: {post.content}")
    return "\n".join(result)

# ========== Agent ==========
scheduler_agent = Agent(
    name="SchedulerAgent",
    instructions="""
You are the Scheduler Agent. You queue social media/blog posts across platforms.

✅ Input: a list of posts with optional scheduled times
🛠️ Use `schedule_posts` to queue posts
⏳ If no time is given, schedule 5 minutes from now
""",
    tools=[schedule_posts],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":
    async def main():
        print("📆 Scheduler Agent Ready!")
        while True:
            platform = input("🛰 Platform (or 'exit'): ").strip()
            if platform.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            content = input("✏️ Content: ").strip()
            scheduled_time = input("⏱ Scheduled Time (optional): ").strip() or None

            post = ScheduledPost(platform=platform, content=content, scheduled_time=scheduled_time)

            result = await Runner.run(
                scheduler_agent,
                [{"role": "user", "content": f"Schedule post to {platform} at {scheduled_time or 'auto'}:\n{content}"}],
                tool_input={"posts": [post]}
            )
            print("\n📢 Result:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation ==========
async def run_scheduler_agent(posts: List[ScheduledPost]) -> str:
    """
    Automation entry point for orchestrator.
    """
    if not posts:
        return "⚠️ No posts provided to schedule."

    result = await Runner.run(
        scheduler_agent,
        [{"role": "user", "content": f"Schedule {len(posts)} post(s)."}],
        tool_input={"posts": posts}
    )
    return result.final_output

# ========== Tool Export ==========
def get_scheduler_agent_tool():
    return scheduler_agent.as_tool(
        tool_name="scheduler_agent",
        tool_description="Schedules content posts to multiple platforms at specified times."
    )
