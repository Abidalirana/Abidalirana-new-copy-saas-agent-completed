# ================================
# 📁 File: orchestrator05.py
# ✅ LLM-Powered Lead Mining Orchestrator (Tool-based)
# ================================

import sys
import os
import asyncio

# ✅ Add root path for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel

# ========== Load Env ========== #
load_dotenv()
set_tracing_disabled(True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is missing in .env")

# ========== Gemini Model Setup ========== #
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# ========== Import Lead Mining Tools ========== #
from myagents.LeadMiningagentstage05.engagerscraperagent import get_engager_scraper_tool
from myagents.LeadMiningagentstage05.icptaggeragent import get_icp_tagger_tool
from myagents.LeadMiningagentstage05.leadenricheragent import get_lead_enricher_tool
from myagents.LeadMiningagentstage05.leadexporteragent import get_lead_exporter_tool
from myagents.LeadMiningagentstage05.messagesuggesteragent import get_message_suggester_tool
from myagents.LeadMiningagentstage05.responsetrackeragent import get_message_suggester_tool

# ========== Load Tools ========== #
engager_tool = get_engager_scraper_tool()
icp_tool = get_icp_tagger_tool()
enricher_tool = get_lead_enricher_tool()
exporter_tool = get_lead_exporter_tool()
suggester_tool = get_message_suggester_tool()
tracker_tool = get_message_suggester_tool()

# ========== Define Orchestrator Agent ========== #
lead_mining_orchestrator = Agent(
    name="LeadMiningOrchestratorAgent",
    instructions="""
You're a Lead Mining Orchestrator Agent. Your job is to take a business goal or targeting idea and generate enriched, export-ready leads with messaging guidance.

🧠 Pipeline Steps:
1. Scrape engaging users (EngagerScraper)
2. Tag ideal customers (ICP Tagger)
3. Enrich with data (LeadEnricher)
4. Prepare for export (LeadExporter)
5. Suggest messages (MessageSuggester)
6. Track responses (ResponseTracker)

🎯 Always call tools in sequence. Take the output of one and feed it to the next.
""",
    tools=[
        engager_tool,
        icp_tool,
        enricher_tool,
        exporter_tool,
        suggester_tool,
        tracker_tool
    ],
    model=model
)

# ========== Export as Tool ========== #
def get_lead_mining_orchestrator_tool():
    return lead_mining_orchestrator.as_tool(
        tool_name="lead_mining_orchestrator",
        tool_description="Runs a multi-step pipeline to mine, enrich, export, and message new leads."
    )

# ========== Optional CLI Runner ========== #
async def run_orchestrator():
    tool_choices = {
        "1": engager_tool,
        "2": icp_tool,
        "3": enricher_tool,
        "4": exporter_tool,
        "5": suggester_tool,
        "6": tracker_tool
    }

    tool_names = {
        "1": "EngagerScraper",
        "2": "ICP Tagger",
        "3": "Lead Enricher",
        "4": "Lead Exporter",
        "5": "Message Suggester",
        "6": "Response Tracker"
    }

    print("\n🛠️ Select which lead mining steps to include:")
    print("1. EngagerScraper\n2. ICP Tagger\n3. Lead Enricher\n4. Lead Exporter\n5. Message Suggester\n6. Response Tracker")
    selected = input("➡️ Enter numbers separated by comma (e.g., 1,2,4 or press Enter for all): ").strip()

    if selected:
        selected_indices = [s.strip() for s in selected.split(",") if s.strip() in tool_choices]
        selected_tools = [tool_choices[i] for i in selected_indices]
        selected_names = [tool_names[i] for i in selected_indices]
    else:
        selected_tools = list(tool_choices.values())
        selected_names = list(tool_names.values())

    print(f"✅ Using tools: {', '.join(selected_names)}")

    # Create dynamic orchestrator
    dynamic_orchestrator = Agent(
        name="LeadMiningOrchestratorAgent",
        instructions=lead_mining_orchestrator.instructions,
        tools=selected_tools,
        model=model
    )

    while True:
        input_data = input("\n💡 Enter your targeting keyword/goal (or 'exit' to quit): ").strip()
        if input_data.lower() in ["exit", "quit"]:
            print("👋 Exiting.")
            break

        try:
            result = await Runner.run(dynamic_orchestrator, input_data)
            print("\n📦 Final Output:\n")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error while running orchestrator: {e}")

# ========== Main Entry ========== #
if __name__ == "__main__":
    asyncio.run(run_orchestrator())
