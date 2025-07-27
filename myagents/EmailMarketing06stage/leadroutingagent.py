# ✅ leadroutingagent.py

import os
import asyncio
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
class LeadRoutingInput(BaseModel):
    lead_name: str
    lead_email: str
    lead_status: str  # e.g. hot, cold, not now
    crm_platform: str  # e.g. HubSpot, Salesforce

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Route this lead into the correct CRM segment based on their status.\n"
                f"Lead Name: {self.lead_name}\n"
                f"Email: {self.lead_email}\n"
                f"Status: {self.lead_status}\n"
                f"CRM Platform: {self.crm_platform}\n\n"
                "Determine the correct segment and return a single-line instruction like:\n"
                "'✅ Routed to Priority Leads in Salesforce'"
            )
        }]

# ========== Tool ==========
@function_tool
def route_lead(lead_name: str, lead_email: str, lead_status: str, crm_platform: str) -> str:
    """
    Routes a lead to the appropriate segment within a CRM based on their status.
    """
    try:
        prompt = LeadRoutingInput(
            lead_name=lead_name,
            lead_email=lead_email,
            lead_status=lead_status,
            crm_platform=crm_platform
        ).to_prompt()

        result = asyncio.run(Runner.run(lead_routing_agent, prompt))
        return result.final_output or "⚠️ No routing suggestion returned."
    except Exception as e:
        return f"❌ Error routing lead: {str(e)}"

# ========== Agent ==========
lead_routing_agent = Agent(
    name="LeadRoutingAgent",
    instructions=(
        "You're a CRM segmentation assistant. Your job is to assign leads to the correct CRM bucket based on their status.\n\n"
        "✅ Rules:\n"
        "- If status is 'hot', assign to 'Priority Leads'.\n"
        "- If status is 'not now', assign to 'Follow-up Later'.\n"
        "- Otherwise, assign to 'Cold Leads'.\n"
        "- Always include the CRM platform in the response.\n\n"
        "⚠️ If any key info is missing, reply with a clear warning."
    ),
    tools=[route_lead],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":
    async def main():
        print("🧭 Lead Routing Agent Ready!")
        while True:
            name = input("👤 Lead name (or 'exit'): ").strip()
            if name.lower() in ["exit", "quit"]:
                break
            email = input("📧 Lead email: ").strip()
            status = input("📊 Lead status (hot, cold, not now): ").strip()
            crm = input("🏢 CRM platform (e.g. Salesforce): ").strip()

            try:
                prompt = LeadRoutingInput(
                    lead_name=name,
                    lead_email=email,
                    lead_status=status,
                    crm_platform=crm
                ).to_prompt()
                result = await Runner.run(lead_routing_agent, prompt)
                print("✅ CRM Routing Result:\n", result.final_output)
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(main())

# ========== Automation Entry ==========
async def run_lead_routing_agent(lead_name: str, lead_email: str, lead_status: str, crm_platform: str) -> str:
    try:
        prompt = LeadRoutingInput(
            lead_name=lead_name,
            lead_email=lead_email,
            lead_status=lead_status,
            crm_platform=crm_platform
        ).to_prompt()
        result = await Runner.run(lead_routing_agent, prompt)
        return result.final_output or "⚠️ No routing result returned."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"
#==============================================================
# ========== Tool Wrapper ==========
def get_lead_routing_tool():
    """
    Expose this agent as a callable tool inside orchestrators.
    """
    return lead_routing_agent.as_tool(
        tool_name="lead_routing_tool",
        tool_description="Routes a lead into the right CRM segment based on their status."
    )
#===========================================================================