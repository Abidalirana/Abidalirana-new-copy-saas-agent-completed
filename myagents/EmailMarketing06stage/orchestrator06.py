# ========== Email Marketing Orchestrator ========== #

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
from myagents.EmailMarketing06stage.coldemailwriteragent import get_coldemail_writer_tool
from myagents.EmailMarketing06stage.followupsequenceagent import get_follow_up_tool
from myagents.EmailMarketing06stage.emailvalidatoragent import get_email_validator_tool
from myagents.EmailMarketing06stage.emaildeliverabilityagent import get_deliverability_tool
from myagents.EmailMarketing06stage.emailscheduleragent import get_email_scheduler_tool
from myagents.EmailMarketing06stage.replyclassificationagent import get_reply_classification_tool
from myagents.EmailMarketing06stage.leadroutingagent import get_lead_routing_tool
from myagents.EmailMarketing06stage.emailreportgeneratoragent import get_email_report_tool

# ========== Load Tools ========== #
coldemail_tool = get_coldemail_writer_tool()
followup_tool = get_follow_up_tool()
validator_tool = get_email_validator_tool()
deliverability_tool = get_deliverability_tool()
scheduler_tool = get_email_scheduler_tool()
classifier_tool = get_reply_classification_tool()
routing_tool = get_lead_routing_tool()
report_tool = get_email_report_tool()

# ========== Define Orchestrator Agent ========== #
email_orchestrator = Agent(
    name="EmailOrchestratorAgent",
    instructions="""
You are an email marketing pipeline orchestrator. Your job is to coordinate the full campaign process, from writing to scheduling and analyzing performance.

📦 Pipeline Tasks:
- Write cold emails
- Generate follow-up sequences
- Validate email addresses
- Check deliverability
- Schedule campaigns
- Classify replies
- Route leads
- Generate reports

🧠 Rules:
- Always follow the sequence.
- Combine outputs to complete an email campaign.
""",
    tools=[
        coldemail_tool,
        followup_tool,
        validator_tool,
        deliverability_tool,
        scheduler_tool,
        classifier_tool,
        routing_tool,
        report_tool
    ],
    model=model
)

# ========== Export as Tool ========== #
def get_email_orchestrator_tool():
    return email_orchestrator.as_tool(
        tool_name="email_marketing_orchestrator",
        tool_description="Runs an end-to-end email marketing workflow using 8 agents."
    )

# ========== Optional CLI Runner ========== #
async def run_email_orchestrator():
    print("📥 Enter your campaign context (e.g., ICP, offer, timing, replies). Type 'done' to finish:\n")
    context = []
    while True:
        line = input("➤ Input: ")
        if line.lower() in ["done", "exit", "quit"]:
            break
        if line.strip():
            context.append(line.strip())

    if not context:
        print("⚠️ No input provided. Exiting.")
        return

    try:
        result = await Runner.run(email_orchestrator, context)
        print("\n📊 Final Campaign Output:\n")
        print(result.final_output)
    except Exception as e:
        print(f"❌ Error occurred: {e}")

# ========== Main ==========
if __name__ == "__main__":
    asyncio.run(run_email_orchestrator())
