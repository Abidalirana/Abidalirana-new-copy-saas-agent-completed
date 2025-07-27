# ✅ Starting Agent 4: lead_exporter_agent.py

# File: lead_exporter_agent.py
import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
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
class LeadExportInput(BaseModel):
    name: str
    email: str
    crm_system: str

    def query(self):
        return [{"role": "user", "content": f"Export lead {self.name} with email {self.email} to {self.crm_system}."}]

# ========== Tool ==========
@function_tool
def export_lead_to_crm(name: str, email: str, crm_system: str) -> str:
    """
    Simulated CRM export logic for leads.
    """
    if not name or not email or not crm_system:
        return "❌ Missing lead info for export."

    return f"✅ Lead '{name}' exported to {crm_system.upper()} with email {email}."

# ========== Agent ==========
lead_exporter_agent = Agent(
    name="LeadExporterAgent",
    instructions=(
        "You're a CRM Export Agent. Your job is to push enriched lead data to a selected CRM or database.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Use the `export_lead_to_crm` tool.\n"
        "- Show clear result of export operation.\n"
        "- Support CRMs like HubSpot, Salesforce, Zoho, etc.\n\n"
        "✅ Response Format:\n"
        "- Status: Success or Failure\n"
        "- Message: Detailed confirmation."
    ),
    tools=[export_lead_to_crm],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📤 Lead Exporter Agent Ready!")
        while True:
            name = input("👤 Lead Name (or 'exit'): ").strip()
            if name.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break
            email = input("📧 Lead Email: ").strip()
            crm = input("💼 CRM System (e.g., HubSpot): ").strip()

            input_data = [{"role": "user", "content": f"Export lead {name} with email {email} to {crm}."}]

            try:
                result = await Runner.run(lead_exporter_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_lead_exporter_agent(name: str, email: str, crm_system: str) -> str:
    if not all([name, email, crm_system]):
        return "❌ Missing input data for lead export."

    input_data = [{"role": "user", "content": f"Export lead {name} with email {email} to {crm_system}."}]
    try:
        result = await Runner.run(lead_exporter_agent, input_data)
        if not result.final_output:
            return "❌ Export failed or returned empty response."
        return result.final_output
    except Exception as e:
        return f"⚠️ Export failed: {str(e)}"

# 🧪 Uncomment below to simulate
# async def test():
#     res = await run_lead_exporter_agent("Emily Stone", "emily@zylotech.com", "hubspot")
#     print(res)
# asyncio.run(test())
#===================================
# ========== Tool Export ========== #
def get_lead_exporter_tool():
    return lead_exporter_agent.as_tool(
        tool_name="lead_exporter",
        tool_description="Exports enriched lead data to a selected CRM system.",
        
    )

