import sys
import os

# ✅ Add the root directory (2 levels up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel

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

# ========== Import Agent Tool Functions ========== #
from myagents.PaidAdsOrchestrator08stage.abtesteragent import get_abtester_agent_tool
from myagents.PaidAdsOrchestrator08stage.adcopywriteragent import get_ad_copywriter_agent_tool
from myagents.PaidAdsOrchestrator08stage.adreportgeneratoragent import get_ad_report_generator_agent_tool
from myagents.PaidAdsOrchestrator08stage.audiencetargetingagent import get_audience_targeting_agent_tool
from myagents.PaidAdsOrchestrator08stage.campaigndeployeraagent import get_campaign_deployer_agent_tool
from myagents.PaidAdsOrchestrator08stage.campaignIdeaagent import get_campaign_idea_agent_tool
from myagents.PaidAdsOrchestrator08stage.creativebriefagent import get_creative_brief_agent_tool
from myagents.PaidAdsOrchestrator08stage.performanceoptimizeragent import get_performance_optimizer_agent_tool
from myagents.PaidAdsOrchestrator08stage.pixelsetupagent import get_pixel_setup_agent_tool

# ========== Load Tools ========== #
abtester_tool = get_abtester_agent_tool()
adcopywriter_tool = get_ad_copywriter_agent_tool()
adreport_tool = get_ad_report_generator_agent_tool()
audience_tool = get_audience_targeting_agent_tool()
campaign_deployer_tool = get_campaign_deployer_agent_tool()
campaign_idea_tool = get_campaign_idea_agent_tool()
creative_brief_tool = get_creative_brief_agent_tool()
performance_tool = get_performance_optimizer_agent_tool()
pixel_tool = get_pixel_setup_agent_tool()

# ========== Define Orchestrator Agent ========== #
paid_ads_orchestrator = Agent(
    name="PaidAdsOrchestratorAgent",
    instructions="""
You are an expert Paid Ads Marketing Orchestrator.
Use the available tools to:
✅ Suggest campaign ideas
✅ Write ad copy
✅ Define audience targeting
✅ Set up pixel tracking
✅ Deploy campaigns
✅ Optimize performance
✅ Generate reports
✅ Create creative briefs
✅ Propose A/B test scenarios

Always provide clear outputs for each task and include summaries when needed.
""",
    tools=[
        abtester_tool,
        adcopywriter_tool,
        adreport_tool,
        audience_tool,
        campaign_deployer_tool,
        campaign_idea_tool,
        creative_brief_tool,
        performance_tool,
        pixel_tool
    ],
    model=model
)

# ========== Export as Tool ========== #
def get_paid_ads_orchestrator_tool():
    return paid_ads_orchestrator.as_tool(
        tool_name="paid_ads_orchestrator",
        tool_description="Plans and executes paid ads workflows including A/B testing, copywriting, targeting, deployment, and optimization."
    )

# ========== Optional CLI Runner ========== #
async def run_orchestrator():
    while True:
        task = input("\n🧠 Describe your paid ads task (or type 'exit'): ").strip()
        if task.lower() in ["exit", "quit"]:
            print("👋 Exiting Paid Ads Orchestrator.")
            break

        try:
            result = await Runner.run(paid_ads_orchestrator, task)
            print("\n🚀 Orchestrator Output:\n")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error while running orchestrator: {e}")

if __name__ == "__main__":
    asyncio.run(run_orchestrator())
