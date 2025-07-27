# ============================================
# ✅ Agent 1: keywordresearchagent.py
# ============================================

import os
import asyncio
from typing import List
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
class KeywordResearchInput(BaseModel):
    topic: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Generate 5 high-value SEO keyword ideas for the topic: '{self.topic}'.\n"
                "Avoid duplicates and keep them relevant to 2025 trends.\n"
                "Return the suggestions in bullet points."
            )
        }]

# ========== Tool ==========
@function_tool
def get_keyword_ideas(topic: str) -> List[str]:
    """
    Returns 5 SEO keyword suggestions for a given topic.
    """
    try:
        prompt = KeywordResearchInput(topic=topic).to_prompt()
        result = asyncio.run(Runner.run(keyword_agent, prompt))
        return result.final_output or ["⚠️ No keyword suggestions."]
    except Exception as e:
        return [f"❌ Error generating keywords: {str(e)}"]

# ========== Agent ==========
keyword_agent = Agent(
    name="KeywordResearchAgent",
    instructions=(
        "You are an SEO keyword research specialist. Given a topic, suggest 5 high-value keywords "
        "that are relevant for 2025. Ensure suggestions are varied, trend-aware, and useful for blog content or SEO planning.\n"
        "✅ Use bullet format.\n"
        "⚠️ Avoid outdated or irrelevant phrases."
    ),
    tools=[get_keyword_ideas],
    model=model
)

# ========== Automation Entry ==========
async def run_keyword_agent(topic: str) -> List[str]:
    if not topic:
        topic = "SEO"
    try:
        prompt = KeywordResearchInput(topic=topic).to_prompt()
        result = await Runner.run(keyword_agent, prompt)
        return result.final_output or ["⚠️ No keyword suggestions."]
    except Exception as e:
        return [f"❌ Automation Error: {str(e)}"]

# ========== Tool Export ==========
def get_keyword_research_tool():
    return keyword_agent.as_tool(
        tool_name="keyword_research_tool",
        tool_description="Generates SEO keyword ideas for a given topic."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("🔍 Keyword Research Agent Ready!")
        while True:
            topic = input("💡 Enter a topic for keyword research (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            try:
                prompt = KeywordResearchInput(topic=topic).to_prompt()
                result = await Runner.run(keyword_agent, prompt)
                print("\n📈 Keyword Suggestions:\n")
                print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
