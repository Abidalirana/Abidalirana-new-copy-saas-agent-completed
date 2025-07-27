# ✅ replyclassificationagent.py

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
class ReplyClassificationInput(BaseModel):
    reply_text: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Classify this email reply: '{self.reply_text}'\n"
                "Return one of: 'Hot Lead', 'Not Now', or 'Bounce'."
            )
        }]

# ========== Tool ==========
@function_tool
def classify_reply(reply_text: str) -> str:
    """
    Classifies a reply as Hot Lead, Not Now, or Bounce.
    """
    try:
        prompt = ReplyClassificationInput(reply_text=reply_text).to_prompt()
        result = asyncio.run(Runner.run(reply_classification_agent, prompt))
        return result.final_output or "⚠️ No classification returned."
    except Exception as e:
        return f"❌ Error classifying reply: {str(e)}"

# ========== Agent ==========
reply_classification_agent = Agent(
    name="ReplyClassificationAgent",
    instructions=(
        "You're an email classification assistant. Your task is to categorize replies from leads.\n\n"
        "✅ Rules:\n"
        "- If the reply expresses interest or booking, return 'Hot Lead'.\n"
        "- If the reply says maybe later or not now, return 'Not Now'.\n"
        "- If the message is a bounce, error, or unsubscribe, return 'Bounce'.\n"
        "⚠️ Do not guess beyond these categories."
    ),
    tools=[classify_reply],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":
    async def main():
        print("📨 Reply Classification Agent Ready!")
        while True:
            reply = input("✉️ Enter lead's reply (or 'exit'): ").strip()
            if reply.lower() in ["exit", "quit"]:
                break
            try:
                prompt = ReplyClassificationInput(reply_text=reply).to_prompt()
                result = await Runner.run(reply_classification_agent, prompt)
                print("✅ Classification:", result.final_output)
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(main())

# ========== Automation Entry ==========
async def run_reply_classifier(reply_text: str) -> str:
    try:
        prompt = ReplyClassificationInput(reply_text=reply_text).to_prompt()
        result = await Runner.run(reply_classification_agent, prompt)
        return result.final_output or "⚠️ No classification generated."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== Tool Wrapper ==========
def get_reply_classification_tool():
    """
    Expose this agent as a callable tool inside orchestrators.
    """
    return reply_classification_agent.as_tool(
        tool_name="reply_classification_tool",
        tool_description="Classifies a reply as 'Hot Lead', 'Not Now', or 'Bounce'."
    )
