# ============================================
# ✅ Agent 8: seoreportgeneratoragent.py
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
class SEOReportInput(BaseModel):
    website_url: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Generate a professional weekly SEO performance report for the following website:\n\n"
                f"{self.website_url}\n\n"
                "Include insights on:\n"
                "✅ Organic traffic trends\n"
                "✅ Top-performing pages\n"
                "✅ Backlink updates\n"
                "✅ Page speed insights\n"
                "✅ Recommendations for improvement"
            )
        }]

# ========== Tool ==========
@function_tool
def generate_seo_report(website_url: str) -> List[str]:
    """
    Generates an SEO performance summary for a website.
    """
    try:
        prompt = SEOReportInput(website_url=website_url).to_prompt()
        result = asyncio.run(Runner.run(seo_report_agent, prompt))
        return result.final_output or ["⚠️ No SEO report generated."]
    except Exception as e:
        return [f"❌ Error generating SEO report: {str(e)}"]

# ========== Agent ==========
seo_report_agent = Agent(
    name="SEOReportGeneratorAgent",
    instructions=(
        "You are an SEO reporting assistant. Given a website URL, generate a concise weekly SEO summary.\n"
        "Include key performance indicators and recommendations.\n"
        "Use the `generate_seo_report` tool for report generation."
    ),
    tools=[generate_seo_report],
    model=model
)

# ========== Automation Entry ==========
async def run_seo_report_agent(website_url: str) -> List[str]:
    if not website_url:
        website_url = "example.com"
    try:
        prompt = SEOReportInput(website_url=website_url).to_prompt()
        result = await Runner.run(seo_report_agent, prompt)
        return result.final_output or ["⚠️ No SEO report generated."]
    except Exception as e:
        return [f"❌ Automation Error: {str(e)}"]

# ========== Tool Export ==========
def get_seo_report_tool():
    return seo_report_agent.as_tool(
        tool_name="seo_report_generator_tool",
        tool_description="Generates a weekly SEO report for a website URL including traffic, backlinks, speed, and recommendations."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("📈 SEO Report Generator Agent Ready!")
        while True:
            url = input("🌐 Enter website URL (or 'exit'): ").strip()
            if url.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            try:
                prompt = SEOReportInput(website_url=url).to_prompt()
                result = await Runner.run(seo_report_agent, prompt)
                print("\n📊 SEO Report:\n")
                print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
