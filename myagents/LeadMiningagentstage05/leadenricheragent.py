# ✅ Starting Agent 2: lead_enricher_agent.py

# File: lead_enricher_agent.py
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
class LeadInput(BaseModel):
    name: str
    company: str

    def query(self):
        return [{"role": "user", "content": f"Find email and company data for {self.name} at {self.company}."}]

# ========== Tool ==========
@function_tool
def enrich_lead(name: str, company: str) -> dict:
    """
    Simulated enrichment tool using Apollo or Clearbit.
    """
    if not name or not company:
        return {"error": "Missing name or company."}

    # Simulated enriched data
    return {
        "name": name,
        "company": company,
        "email": f"{name.lower().replace(' ', '.')}@{company.lower().replace(' ', '')}.com",
        "position": "Sales Manager",
        "location": "New York, USA"
    }

# ========== Agent ==========
lead_enricher_agent = Agent(
    name="LeadEnricherAgent",
    instructions=(
        "You're a Lead Enrichment Agent. Your job is to retrieve detailed contact information for a given lead.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Always use the `enrich_lead` tool.\n"
        "- Return all found fields clearly: email, position, location.\n"
        "- If missing data, show fallback message.\n\n"
        "✅ Response Format:\n"
        "- Name: [name]\n"
        "- Company: [company]\n"
        "- Email: [email]\n"
        "- Position: [position]\n"
        "- Location: [location]"
    ),
    tools=[enrich_lead],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🔍 Lead Enricher Agent Ready!")
        while True:
            name = input("👤 Enter lead's full name (or 'exit'): ").strip()
            if name.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break
            company = input("🏢 Enter company name: ").strip()

            try:
                input_data = [{"role": "user", "content": f"Find email and company data for {name} at {company}."}]
                result = await Runner.run(lead_enricher_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_lead_enricher_agent(name: str, company: str) -> str:
    if not name or not company:
        return "❌ Name or company missing."

    input_data = [{"role": "user", "content": f"Find email and company data for {name} at {company}."}]
    try:
        result = await Runner.run(lead_enricher_agent, input_data)
        if not result.final_output:
            return "❌ No enrichment data found."
        return result.final_output
    except Exception as e:
        return f"⚠️ Failed to enrich lead: {str(e)}"

# 🧪 Uncomment below to test
# async def test():
#     response = await run_lead_enricher_agent("Alice Walker", "TechCorp")
#     print(response)
# asyncio.run(test())
#===============
# ========== Tool Export ========== #
def get_lead_enricher_tool():
    return lead_enricher_agent.as_tool(
        tool_name="lead_enricher",
        tool_description="Enriches a lead with email, position, and location using name and company.",
        
    )

