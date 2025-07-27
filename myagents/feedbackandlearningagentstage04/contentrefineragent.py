# ✅ Agent 03: ContentRefinerAgent
# 📁 File: myagents/feedbackandlearningagents05/contentrefineragent.py

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
class PostFeedback(BaseModel):
    post_text: str
    feedback: str

    def to_messages(self):
        return [{
            "role": "user",
            "content": f"Refine this post based on feedback.\n\nPost: {self.post_text}\nFeedback: {self.feedback}"
        }]

# ========== Tools ==========
@function_tool
def refine_post_content(post_text: str, feedback: str) -> str:
    """
    Suggest improvements to post content based on user feedback.
    """
    refined = f"🔧 Improved Post:\n{post_text} (now includes user suggestions like clarity, tone fix, or added detail)"
    return refined

# ========== Agent ==========
refiner_agent = Agent(
    name="ContentRefinerAgent",
    instructions=(
        "You're a smart assistant that refines post content using real user feedback.\n\n"
        "🧠 Rules:\n"
        "- Always use `refine_post_content` tool to improve the post.\n"
        "- Focus on feedback: clarify message, adjust tone, or add value.\n"
        "- Return a polished post with labeled heading.\n"
        "- Do NOT just repeat the post or feedback."
    ),
    tools=[refine_post_content],
    model=model
)

# ========== Automation Entry Point ==========
# 👉 This function is called from orchestrator
async def run_refiner_agent(post_text: str = "", feedback: str = "") -> str:
    try:
        input_data = PostFeedback(
            post_text=post_text,
            feedback=feedback
        ).to_messages()
        result = await Runner.run(refiner_agent, input_data)
        return result.final_output
    except Exception as e:
        fallback_msg = (
            f"⚠️ Fallback triggered: {str(e)}\n"
            "✍️ Could not refine with model, but here's a tip: Focus on making your message more concise and persuasive."
        )
        return fallback_msg

# 🧪 Manual test runner (optional)
if __name__ == "__main__":

    async def main():
        print("🛠️ Content Refiner Agent Ready!")
        while True:
            post = input("📝 Enter original post (or 'exit'): ")
            if post.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break
            feedback = input("💬 Enter feedback for this post: ")
            input_data = PostFeedback(
                post_text=post,
                feedback=feedback
            ).to_messages()
            result = await Runner.run(refiner_agent, input_data)
            print(result.final_output)

    asyncio.run(main())