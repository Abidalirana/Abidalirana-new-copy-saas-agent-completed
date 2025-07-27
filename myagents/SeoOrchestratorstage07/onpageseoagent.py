# ============================================
# ✅ Agent 4: onpageseoagent.py
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
class OnPageSEOInput(BaseModel):
    page_content: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                "Perform an on-page SEO audit of the following HTML content:\n\n"
                f"{self.page_content}\n\n"
                "✅ Check for H1 tag presence.\n"
                "✅ Check for meta tags.\n"
                "✅ Detect schema markup.\n"
                "Return results in a readable checklist format."
            )
        }]

# ========== Tool ==========
@function_tool
def analyze_onpage_seo(content: str) -> List[str]:
    """
    Performs a basic on-page SEO audit on HTML content.
    """
    try:
        prompt = OnPageSEOInput(page_content=content).to_prompt()
        result = asyncio.run(Runner.run(onpageseo_agent, prompt))
        return result.final_output or ["⚠️ No SEO audit results."]
    except Exception as e:
        return [f"❌ Error in SEO audit: {str(e)}"]

# ========== Agent ==========
onpageseo_agent = Agent(
    name="OnPageSEOAgent",
    instructions=(
        "You are an On-Page SEO specialist. Analyze the provided HTML content for SEO signals.\n"
        "✅ Check for proper H1 tags, meta tags, and structured data (schema markup).\n"
        "⚠️ Be concise and specific in feedback.\n"
        "Use the `analyze_onpage_seo` tool for the audit."
    ),
    tools=[analyze_onpage_seo],
    model=model
)

# ========== Automation Entry ==========
async def run_onpageseo_agent(content: str) -> List[str]:
    if not content:
        content = "<html><head><title>Untitled</title></head><body>No SEO tags here</body></html>"
    try:
        prompt = OnPageSEOInput(page_content=content).to_prompt()
        result = await Runner.run(onpageseo_agent, prompt)
        return result.final_output or ["⚠️ No SEO audit results."]
    except Exception as e:
        return [f"❌ Automation Error: {str(e)}"]

# ========== Tool Export ==========
def get_onpage_seo_tool():
    return onpageseo_agent.as_tool(
        tool_name="onpage_seo_audit_tool",
        tool_description="Audits HTML content for on-page SEO elements like H1 tags, meta tags, and schema."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("🔍 On-Page SEO Agent Ready!")
        while True:
            content = input("📄 Enter HTML content (or 'exit'): ").strip()
            if content.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            try:
                prompt = OnPageSEOInput(page_content=content).to_prompt()
                result = await Runner.run(onpageseo_agent, prompt)
                print("\n🧾 SEO Audit Result:\n")
                print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
