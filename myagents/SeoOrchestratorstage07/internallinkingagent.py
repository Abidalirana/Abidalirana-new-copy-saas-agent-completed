# ============================================
# ✅ Agent 5: internallinkingagent.py
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
class InternalLinkingInput(BaseModel):
    page_content: str
    site_pages: List[str]

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Suggest relevant internal links for the following page content:\n\n"
                f"{self.page_content}\n\n"
                f"Available site pages to link to: {', '.join(self.site_pages)}\n\n"
                "Identify phrases or keywords in the content that can naturally link to other pages."
            )
        }]

# ========== Tool ==========
@function_tool
def suggest_internal_links(page_content: str, site_pages: List[str]) -> List[str]:
    """
    Suggests internal links from content to site pages based on keyword matches.
    """
    try:
        prompt = InternalLinkingInput(page_content=page_content, site_pages=site_pages).to_prompt()
        result = asyncio.run(Runner.run(internal_link_agent, prompt))
        return result.final_output or ["⚠️ No internal linking suggestions."]
    except Exception as e:
        return [f"❌ Error generating links: {str(e)}"]

# ========== Agent ==========
internal_link_agent = Agent(
    name="InternalLinkingAgent",
    instructions=(
        "You are an internal linking expert. Given the page content and site structure, "
        "suggest appropriate internal links based on semantic and keyword relevance.\n"
        "✅ Identify useful internal linking opportunities.\n"
        "⚠️ Avoid overlinking or irrelevant suggestions."
    ),
    tools=[suggest_internal_links],
    model=model
)

# ========== Automation Entry ==========
async def run_internal_link_agent(content: str, pages: List[str]) -> List[str]:
    try:
        prompt = InternalLinkingInput(page_content=content, site_pages=pages).to_prompt()
        result = await Runner.run(internal_link_agent, prompt)
        return result.final_output or ["⚠️ No internal linking suggestions."]
    except Exception as e:
        return [f"❌ Automation Error: {str(e)}"]

# ========== Tool Export ==========
def get_internal_linking_tool():
    return internal_link_agent.as_tool(
        tool_name="internal_linking_tool",
        tool_description="Suggests internal links based on page content and existing site pages."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("🔗 Internal Linking Agent Ready!")
        while True:
            content = input("📄 Enter page content (or 'exit'): ").strip()
            if content.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            pages_input = input("📚 Enter site page titles separated by commas: ").strip()
            site_pages = [p.strip() for p in pages_input.split(",") if p.strip()]

            try:
                prompt = InternalLinkingInput(page_content=content, site_pages=site_pages).to_prompt()
                result = await Runner.run(internal_link_agent, prompt)
                print("\n🔍 Internal Linking Suggestions:\n")
                print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
