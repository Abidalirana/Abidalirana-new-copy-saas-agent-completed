# =======================
# 📁 File: myagents/feedbackandlearningagents05/engagementmonitor_agent.py
# =======================

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
class EngagementData(BaseModel):
    likes: int
    comments: int
    shares: int
    ctr: float  # Click-through rate (%)

    def to_messages(self):
        return [{
            "role": "user",
            "content": f"Evaluate post engagement with {self.likes} likes, "
                       f"{self.comments} comments, {self.shares} shares, and {self.ctr}% CTR."
        }]

# ========== Tool ==========
@function_tool
def summarize_engagement(likes: int, comments: int, shares: int, ctr: float) -> str:
    """
    Summarizes social media engagement based on likes, comments, shares, and CTR.
    """
    score = likes + (2 * comments) + (3 * shares) + (ctr * 10)
    if score > 100:
        return "🔥 This post is performing exceptionally well across all metrics."
    elif score > 50:
        return "👍 This post has moderate engagement."
    else:
        return "⚠️ This post has low engagement. Consider improving visuals or copy."

# ========== Agent ==========
engagement_monitor_agent = Agent(
    name="EngagementMonitorAgent",
    instructions=(
        "You analyze social media post engagement based on likes, comments, shares, and click-through rate (CTR).\n\n"
        "📊 Analysis Rules:\n"
        "- Use the `summarize_engagement` tool to classify engagement.\n"
        "- Deliver a helpful summary: High, Medium, or Low.\n"
        "- Provide actionable insight if performance is low.\n\n"
        "✅ Format:\n"
        "- Emoji indicator (🔥, 👍, ⚠️)\n"
        "- Clear single-sentence summary"
    ),
    tools=[summarize_engagement],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":

    async def main():
        print("📊 Engagement Monitor Agent Ready!")
        while True:
            try:
                likes = int(input("❤️ Likes: "))
                comments = int(input("💬 Comments: "))
                shares = int(input("🔁 Shares: "))
                ctr = float(input("📈 CTR (%): "))
            except ValueError:
                print("❌ Invalid input. Try again.")
                continue

            input_data = EngagementData(
                likes=likes,
                comments=comments,
                shares=shares,
                ctr=ctr
            ).to_messages()

            result = await Runner.run(engagement_monitor_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Function ==========
async def run_engagement_monitor_agent(likes: int, comments: int, shares: int, ctr: float) -> str:
    try:
        input_data = EngagementData(
            likes=likes,
            comments=comments,
            shares=shares,
            ctr=ctr
        ).to_messages()

        result = await Runner.run(engagement_monitor_agent, input_data)
        return result.final_output

    except Exception as e:
        print(f"⚠️ Fallback Triggered: {e}")
        # ✅ Simple fallback using logic
        try:
            fallback_summary = summarize_engagement(likes, comments, shares, ctr)
            return f"🔁 [Fallback Summary]: {fallback_summary}"
        except Exception as inner_e:
            return f"❌ Fallback also failed: {inner_e}"

# ========== Tool Export ==========
def get_engagement_monitor_tool():
    return engagement_monitor_agent.as_tool(
        tool_name="monitor_engagement",
        tool_description="Analyze post engagement using metrics like likes, comments, shares, and CTR."
    )
