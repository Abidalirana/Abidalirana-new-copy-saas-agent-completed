# ✅ orchestrator07.py

import sys
import os

# Add project root to sys.path (2 levels up)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
import os
from agents import Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

# ========== Load Environment ==========
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

# ========== Import Tools ==========
from myagents.SeoOrchestratorstage07.backlinkoutreachagent import get_backlink_outreach_tool
from myagents.SeoOrchestratorstage07.blogoptimizeragent import  get_blogoptimizer_tool
from myagents.SeoOrchestratorstage07.blogwriteragent import get_blog_writer_tool
from myagents.SeoOrchestratorstage07.clusterbuilderagent import get_cluster_builder_tool
from myagents.SeoOrchestratorstage07.internallinkingagent import get_internal_linking_tool
from myagents.SeoOrchestratorstage07.keywordresearchagent import get_keyword_research_tool
from myagents.SeoOrchestratorstage07.onpageseoagent import get_onpage_seo_tool
from myagents.SeoOrchestratorstage07.seoreportgeneratoragen import get_seo_report_tool
from myagents.SeoOrchestratorstage07.technicalseoagent import get_technical_seo_tool

# ========== Load Tools ==========
tools = [
    get_backlink_outreach_tool(),
     get_blogoptimizer_tool(),
    get_blog_writer_tool(),
    get_cluster_builder_tool(),
    get_internal_linking_tool(),
    get_keyword_research_tool(),
    get_onpage_seo_tool(),
    get_seo_report_tool(),
    get_technical_seo_tool()
]

# ========== Define SEO Orchestrator ==========
seo_orchestrator = Agent(
    name="SeoOrchestratorStage07",
    instructions="""
You are an SEO Automation Orchestrator. Your job is to coordinate all SEO tasks including backlink outreach, blog writing, on-page optimization, internal linking, technical audits, and reporting.

✅ Rules:
- Use each tool for its specific SEO task.
- If input is too vague, ask for clarification.
- Combine relevant insights across tools.
- Output a short strategy summary based on the tools used.
""",
    tools=tools,
    model=model
)

# ========== Export as Tool ==========
def get_seo_orchestrator_tool():
    return seo_orchestrator.as_tool(
        tool_name="seo_orchestrator_tool",
        tool_description="Coordinates and executes multiple SEO automation agents"
    )

# ========== Optional CLI Runner ==========
async def run_orchestrator():
    print("\n🧠 SEO Orchestrator Ready!")
    while True:
        task = input("📝 Enter SEO task or keyword (or type 'exit'): ").strip()
        if task.lower() in ["exit", "quit"]:
            print("👋 Exiting.")
            break

        try:
            result = await Runner.run(seo_orchestrator, task)
            print("\n✅ Final SEO Strategy:\n")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error running orchestrator: {e}")

if __name__ == "__main__":
    asyncio.run(run_orchestrator())
