# ✅ Agent 02: ContentPerformanceAgent
# 📁 File: myagents/feedbackandlearningagents05/contentperformanceagent.py

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
class PostMetrics(BaseModel):
    post_text: str
    impressions: int
    likes: int
    comments: int
    shares: int
    saves: int

    def to_messages(self):
        return [{
            "role": "user",
            "content": f"Evaluate the performance of this post: {self.post_text}\n"
                       f"Impressions: {self.impressions}, Likes: {self.likes}, Comments: {self.comments}, "
                       f"Shares: {self.shares}, Saves: {self.saves}"
        }]

# ========== Tools ==========
@function_tool
def score_post_performance(impressions: int, likes: int, comments: int, shares: int, saves: int) -> str:
    """
    Scores social media post performance based on weighted metrics.
    """
    if impressions == 0:
        return "⚠️ Cannot evaluate performance — impressions count is zero."

    engagement = likes + comments + shares + saves
    score = (engagement / impressions) * 100
    summary = (
        f"Post Performance Evaluation:\n"
        f"- Impressions: {impressions}\n"
        f"- Likes: {likes}\n"
        f"- Comments: {comments}\n"
        f"- Shares: {shares}\n"
        f"- Saves: {saves}\n"
        f"- Engagement Rate: {score:.2f}%"
    )
    return summary

# ========== Agent ==========
performance_agent = Agent(
    name="ContentPerformanceAgent",
    instructions=(
        "You're an assistant that scores the overall performance of a social media post.\n\n"
        "🧠 Rules:\n"
        "- Use `score_post_performance` tool to compute the engagement rate.\n"
        "- If impressions are 0, return a warning message.\n"
        "- Always show all the metrics clearly.\n"
        "- Use friendly and professional tone.\n"
        "- Output must have bullet format with labels."
    ),
    tools=[score_post_performance],
    model=model
)

# ========== Automation Entry Point ==========
# 👉 This function is called from orchestrator
async def run_performance_agent(post_text: str = "", impressions: int = 0, likes: int = 0, comments: int = 0, shares: int = 0, saves: int = 0) -> str:
    try:
        input_data = PostMetrics(
            post_text=post_text,
            impressions=impressions,
            likes=likes,
            comments=comments,
            shares=shares,
            saves=saves
        ).to_messages()
        result = await Runner.run(performance_agent, input_data)
        return result.final_output
    except Exception as e:
        fallback_msg = (
            f"⚠️ Fallback triggered: {str(e)}\n"
            "📉 Unable to process detailed metrics. Here's a basic tip:\n"
            "Try highlighting a clear CTA and using more relevant hashtags to improve performance."
        )
        return fallback_msg

# 🧪 Manual test runner (optional)
if __name__ == "__main__":

    async def main():
        print("📊 Content Performance Agent Ready!")
        while True:
            text = input("📝 Enter post text (or type 'exit'): ")
            if text.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break
            try:
                impressions = int(input("Impressions: ") or 0)
                likes = int(input("Likes: ") or 0)
                comments = int(input("Comments: ") or 0)
                shares = int(input("Shares: ") or 0)
                saves = int(input("Saves: ") or 0)
            except ValueError:
                print("❌ Invalid input. Please enter numeric values.")
                continue

            input_data = PostMetrics(
                post_text=text,
                impressions=impressions,
                likes=likes,
                comments=comments,
                shares=shares,
                saves=saves
            ).to_messages()
            result = await Runner.run(performance_agent, input_data)
            print(result.final_output)

    asyncio.run(main())
#====================================================
# ========== Export as Tool ========== #
def get_content_performance_tool():
    return performance_agent.as_tool(
        tool_name="content_performance",
        tool_description="Analyzes social media content metrics (impressions, likes, shares, etc.) and returns a performance score with insights"
    )
#==================================
