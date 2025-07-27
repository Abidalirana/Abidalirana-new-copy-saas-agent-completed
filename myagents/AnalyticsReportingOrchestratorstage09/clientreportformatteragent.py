# ✅ Agent: clientreportformatteragent.py

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
class ReportInput(BaseModel):
    client_name: str
    campaign_summary: str

# ========== Tool ==========
@function_tool
def format_report(client_name: str, campaign_summary: str) -> str:
    """
    Formats a campaign summary for client reporting.
    """
    try:
        return f"📄 Client: {client_name}\n\n📝 Campaign Summary:\n{campaign_summary.strip()}"
    except Exception as e:
        return f"⚠️ Error formatting report: {str(e)}"

# ========== Agent ==========
report_formatter_agent = Agent(
    name="ClientReportFormatterAgent",
    instructions=(
        "You're a report formatter for clients.\n"
        "Always use format_report to structure campaign summaries professionally."
    ),
    tools=[format_report],
    model=model
)

# ========== Tool Wrapper for Orchestrator ==========
def get_client_report_formatter_tool():
    """
    Exposes ClientReportFormatterAgent as a tool for orchestrators.
    """
    return report_formatter_agent.as_tool(
        tool_name="client_report_formatter_agent",
        tool_description="Formats campaign summaries into professional client-ready reports."
    )

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📋 Client Report Formatter Agent Ready!")
        while True:
            client = input("Enter client name or 'exit': ").strip()
            if client.lower() in ["exit", "quit"]:
                break
            summary = input("Enter campaign summary: ").strip()
            input_data = [{"role": "user", "content": f"Format report for {client}: {summary}"}]
            result = await Runner.run(report_formatter_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_client_report_formatter(client_name: str, campaign_summary: str) -> str:
    if not client_name or not campaign_summary:
        return "⚠️ Client name and summary required."
    input_data = [{"role": "user", "content": f"Format report for {client_name}: {campaign_summary}"}]
    try:
        result = await Runner.run(report_formatter_agent, input_data)
        return result.final_output or "⚠️ Report formatting failed."
    except Exception as e:
        return f"⚠️ Client Report Formatter Agent failed: {str(e)}"
