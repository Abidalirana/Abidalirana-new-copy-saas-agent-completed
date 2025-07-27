import sys
import os

# ✅ Add the root directory (2 levels up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
from agents import Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

# ========== Load Env ========== #
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

# ========== Import Tools ========== #
from myagents.AnalyticsReportingOrchestratorstage09.attributionagent import get_attribution_agent_tool
from myagents.AnalyticsReportingOrchestratorstage09.clientreportformatteragent import get_client_report_formatter_tool
from myagents.AnalyticsReportingOrchestratorstage09.contentperformanceagent import get_content_performance_tool
from myagents.AnalyticsReportingOrchestratorstage09.funneldropoffdetectoragent import get_funnel_dropoff_detector_tool
from myagents.AnalyticsReportingOrchestratorstage09.kpitrackeragent import get_kpi_tracker_tool
from myagents.AnalyticsReportingOrchestratorstage09.leadpipelineanalyzeragent import get_lead_pipeline_analyzer_tool

# ========== Load Tools ========== #
attribution_tool = get_attribution_agent_tool()
report_formatter_tool = get_client_report_formatter_tool()
content_perf_tool = get_content_performance_tool()
dropoff_tool = get_funnel_dropoff_detector_tool()
kpi_tracker_tool = get_kpi_tracker_tool()
lead_pipeline_tool = get_lead_pipeline_analyzer_tool()

# ========== Define Orchestrator Agent ========== #
analytics_orchestrator = Agent(
    name="AnalyticsReportingOrchestratorAgent",
    instructions="""
You are an Analytics and Reporting Orchestrator Agent. You coordinate multiple sub-agents to:
- Track KPIs
- Detect funnel drop-offs
- Analyze content performance
- Format reports for clients
- Attribute leads to sources
- Examine lead pipelines

🧠 Instructions:
- Always use all available tools.
- Provide a concise, business-friendly summary.
- Ensure consistency across all metrics and findings.
- Avoid technical jargon, explain insights clearly.
""",
    tools=[
        attribution_tool,
        report_formatter_tool,
        content_perf_tool,
        dropoff_tool,
        kpi_tracker_tool,
        lead_pipeline_tool
    ],
    model=model
)

# ========== Export as Tool ========== #
def get_analytics_orchestrator_tool():
    return analytics_orchestrator.as_tool(
        tool_name="analytics_reporting_orchestrator",
        tool_description="Aggregates KPI tracking, funnel analysis, attribution, reporting, and lead analysis."
    )

# ========== Optional CLI Runner ========== #
async def run_orchestrator():
    print("\n📊 Analytics Reporting Orchestrator Ready!")
    print("(Type 'exit' to quit)")

    while True:
        user_input = input("\n📥 Enter analytics summary request: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting. Goodbye!")
            break

        if not user_input:
            print("⚠️ Please enter a valid request.")
            continue

        try:
            result = await Runner.run(analytics_orchestrator, user_input)
            print("\n📈 Final Report Output:\n")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error while running orchestrator: {e}")


if __name__ == "__main__":
    asyncio.run(run_orchestrator())
