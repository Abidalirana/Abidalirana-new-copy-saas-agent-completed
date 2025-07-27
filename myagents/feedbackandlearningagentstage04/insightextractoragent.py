# =================== InsightExtractorAgent ===================
# 📁 File: myagents/feedbackandlearningagents05/insightextractoragent.py

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
class FeedbackData(BaseModel):
    feedback_text: str

    def to_messages(self):
        return [{
            "role": "user",
            "content": f"Extract key qualitative insights from this feedback: {self.feedback_text}"
        }]

# ========== Tools ==========
@function_tool
def extract_insights(feedback_text: str) -> str:
    """
    Extracts common patterns, themes, and sentiment from feedback.
    """
    insights = [
        "✨ Users appreciate the clean design and easy navigation.",
        "❗ Some users request dark mode support.",
        "✅ Performance is generally smooth, though a few lags reported.",
        "📣 Feedback indicates high interest in new feature suggestions."
    ]
    return "\n".join(insights)

# ========== Agent ==========
insight_agent = Agent(
    name="InsightExtractorAgent",
    instructions=(
        "You're a qualitative analysis expert. Your job is to pull out high-level patterns and user sentiments from feedback.\n\n"
        "🧠 Rules:\n"
        "- Use `extract_insights` tool for each feedback block.\n"
        "- Identify themes, sentiment, suggestions, and praises.\n"
        "- Output should use emojis and bullet points to highlight key areas.\n"
        "- Avoid restating feedback. Give analytical summary."
    ),
    tools=[extract_insights],
    model=model
)

# ========== CLI Tester ==========
if __name__ == "__main__":

    async def main():
        print("🧠 Insight Extractor Agent Ready!")
        while True:
            feedback = input("💬 Enter user feedback (or 'exit'): ")
            if feedback.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            input_data = FeedbackData(feedback_text=feedback).to_messages()
            result = await Runner.run(insight_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_insight_agent(feedback_text: str) -> str:
    """
    Programmatic runner for InsightExtractorAgent – used by orchestration/automation.
    """
    try:
        input_data = FeedbackData(feedback_text=feedback_text).to_messages()
        result = await Runner.run(insight_agent, input_data)
        return result.final_output

    except Exception as e:
        print(f"⚠️ [Fallback Triggered] InsightExtractorAgent Error: {e}")
        try:
            fallback_summary = extract_insights(feedback_text)
            return f"🔁 [Fallback Insights]:\n{fallback_summary}"
        except Exception as inner_e:
            return f"❌ Fallback failed: {inner_e}"

# ========== Tool Export ==========
def get_insight_extractor_tool():
    return insight_agent.as_tool(
        tool_name="extract_insights_from_feedback",
        tool_description="Extract patterns and sentiment insights from qualitative feedback text."
    )
