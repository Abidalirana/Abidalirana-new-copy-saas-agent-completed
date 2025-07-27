# ============================================
# ✅ Agent 6: technicalseoagent.py
# ============================================

import os
import asyncio
from typing import List, Dict, Union
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
class TechnicalSEOInput(BaseModel):
    website_url: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Perform a technical SEO audit for the following website:\n\n"
                f"{self.website_url}\n\n"
                "✅ Evaluate Core Web Vitals\n"
                "✅ Check sitemap and robots.txt\n"
                "✅ Mobile-friendliness\n"
                "✅ HTTPS usage\n"
                "✅ Page speed performance"
            )
        }]

# ========== Tool ==========
@function_tool
def perform_technical_seo_audit(website_url: str) -> Dict[str, str]:
    """
    Simulates a technical SEO audit for the given website URL.
    """
    try:
        return {
            "Core Web Vitals": "Good (LCP: 2.5s, FID: 15ms, CLS: 0.1)",
            "Sitemap": "Sitemap.xml present and valid",
            "Robots.txt": "No issues found",
            "Mobile Friendly": "Yes, passes mobile usability tests",
            "Page Speed": "85/100 on Google PageSpeed Insights",
            "HTTPS": "Secure with valid SSL certificate"
        }
    except Exception:
        return {"Error": "⚠️ Fallback: Could not perform technical SEO audit."}

# ========== Agent ==========
technical_seo_agent = Agent(
    name="TechnicalSEOAgent",
    instructions=(
        "You are a technical SEO expert. Given a website URL, analyze its Core Web Vitals, sitemap, robots.txt, HTTPS, and mobile optimization.\n"
        "Use the `perform_technical_seo_audit` tool to generate a detailed audit report."
    ),
    tools=[perform_technical_seo_audit],
    model=model
)

# ========== Automation Entry ==========
async def run_technical_seo_agent(url: str) -> Union[Dict[str, str], str]:
    if not url:
        url = "https://example.com"
    try:
        prompt = TechnicalSEOInput(website_url=url).to_prompt()
        result = await Runner.run(technical_seo_agent, prompt)
        return result.final_output or {"⚠️": "No audit results returned."}
    except Exception as e:
        return {"❌ Error": str(e)}

# ========== Tool Export ==========
def get_technical_seo_tool():
    return technical_seo_agent.as_tool(
        tool_name="technical_seo_audit_tool",
        tool_description="Performs a technical SEO audit on a website, including Core Web Vitals, sitemap, HTTPS, and mobile usability."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("🛠️ Technical SEO Agent Ready!")
        while True:
            url = input("🌐 Enter website URL for audit (or 'exit'): ").strip()
            if url.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break
            try:
                prompt = TechnicalSEOInput(website_url=url).to_prompt()
                result = await Runner.run(technical_seo_agent, prompt)
                print("\n🔍 Technical SEO Audit Result:\n")
                if isinstance(result.final_output, dict):
                    for key, value in result.final_output.items():
                        print(f"- {key}: {value}")
                else:
                    print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
