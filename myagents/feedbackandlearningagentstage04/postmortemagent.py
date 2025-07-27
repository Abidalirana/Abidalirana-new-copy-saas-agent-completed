# =======================
# 📁 File: myagents/feedbackandlearningagents05/postmortemagent.py
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
class PostSummaryInput(BaseModel):
    post_data: list[str]  # Each string is post metadata and result

    def to_messages(self):
        return [{
            "role": "user",
            "content": f"Summarize weekly post data: {self.post_data}"
        }]

# ========== Tools ==========
@function_tool()
def summarize_weekly_posts(post_data: list[str]) -> str:
    """
    Summarizes high and low performing posts for the week.
    """
    print("📊 Analyzing post history...")
    return (
        "📅 Weekly Post-Mortem Summary:\n"
        "✅ Top Performers:\n"
        "- 'How AI is changing careers' (CTR 12%, 220 likes)\n"
        "- 'Remote work hacks' (CTR 10%, 190 likes)\n"
        "❌ Underperformers:\n"
        "- 'My morning routine' (CTR 2%, 30 likes)\n"
        "- 'Productivity checklist' (CTR 3%, 45 likes)"
    )

# ========== Agent ==========
postmortem_agent = Agent(
    name="PostMortemAgent",
    instructions=(
        "You summarize LinkedIn content performance at the end of the week.\n\n"
        "📌 Intelligence Rules:\n"
        "- Always call `summarize_weekly_posts` on a batch.\n"
        "- Clearly distinguish top vs underperforming posts.\n"
        "- Highlight CTR or like-based metrics.\n\n"
        "✅ Response Format:\n"
        "- Title: Weekly Post-Mortem Summary\n"
        "- Use bullet points under 'Top Performers' and 'Underperformers'"
    ),
    tools=[summarize_weekly_posts],
    model=model
)

# ========== CLI Tester ==========
if __name__ == "__main__":

    async def main():
        print("📅 Post-Mortem Agent Ready!")
        while True:
            raw_data = input("📑 Paste weekly post results (semicolon-separated): ").strip()
            if raw_data.lower() in ["exit", "quit"]:
                print("👋 Exiting Post-Mortem Agent.")
                break
            post_data = [s.strip() for s in raw_data.split(";") if s.strip()]
            input_data = PostSummaryInput(post_data=post_data).to_messages()
            result = await Runner.run(postmortem_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_postmortem_agent(post_data: list[str]) -> str:
    """
    Automation trigger to summarize weekly post performance.
    """
    try:
        input_data = PostSummaryInput(post_data=post_data).to_messages()
        result = await Runner.run(postmortem_agent, input_data)
        return result.final_output
    except Exception as e:
        print(f"⚠️ [Fallback Triggered] PostMortemAgent Error: {e}")
        try:
            fallback_summary = summarize_weekly_posts(post_data)
            return f"🔁 [Fallback Summary]:\n{fallback_summary}"
        except Exception as inner_e:
            return f"❌ Failed in both LLM and fallback: {inner_e}"

# ========== Tool Export ==========
def get_postmortem_agent_tool():
    return postmortem_agent.as_tool(
        tool_name="summarize_linkedin_post_batch",
        tool_description="Summarize top and underperforming LinkedIn posts using CTR and likes."
    )
