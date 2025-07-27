# ============================================
# ✅ Agent 7: backlinkoutreachagent.py
# ============================================

import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List

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
class BacklinkOutreachInput(BaseModel):
    niche: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Generate backlink outreach message templates for the '{self.niche}' niche.\n"
                "Return 4–5 creative suggestions targeting bloggers, content creators, or site owners.\n"
                "Focus on relevance, personalization, and value exchange."
            )
        }]

# ========== Tool ==========
@function_tool
def generate_backlink_outreach_messages(niche: str) -> List[str]:
    """
    Generates backlink outreach suggestions based on the niche.
    """
    try:
        prompt = BacklinkOutreachInput(niche=niche).to_prompt()
        result = asyncio.run(Runner.run(backlink_outreach_agent, prompt))
        return result.final_output or ["⚠️ No messages generated."]
    except Exception as e:
        return [f"❌ Error generating messages: {str(e)}"]

# ========== Agent ==========
backlink_outreach_agent = Agent(
    name="BacklinkOutreachAgent",
    instructions=(
        "You're a backlink outreach specialist. Given a niche, your job is to generate persuasive backlink outreach message templates.\n"
        "✅ Focus:\n"
        "- Personalization\n"
        "- Value proposition\n"
        "- Guest posts, expert quotes, link exchange, and follow-ups.\n"
        "⚠️ Output should be clear, relevant, and actionable."
    ),
    tools=[generate_backlink_outreach_messages],
    model=model
)

# ========== Automation Entry ==========
async def run_backlink_outreach_agent(niche: str) -> List[str]:
    try:
        prompt = BacklinkOutreachInput(niche=niche).to_prompt()
        result = await Runner.run(backlink_outreach_agent, prompt)
        return result.final_output or ["⚠️ No outreach messages generated."]
    except Exception as e:
        return [f"❌ Automation Error: {str(e)}"]

# ========== Tool Export ==========
def get_backlink_outreach_tool():
    return backlink_outreach_agent.as_tool(
        tool_name="backlink_outreach_generator",
        tool_description="Generates outreach message templates for backlink building based on a given niche."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("🔗 Backlink Outreach Agent Ready!")
        while True:
            niche = input("📢 Enter niche for backlink outreach (or 'exit'): ").strip()
            if niche.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            try:
                prompt = BacklinkOutreachInput(niche=niche).to_prompt()
                result = await Runner.run(backlink_outreach_agent, prompt)
                print("\n📧 Suggested Messages:")
                if isinstance(result.final_output, list):
                    for msg in result.final_output:
                        print(f"- {msg}")
                else:
                    print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
