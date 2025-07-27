# ✅ Agent: leadpipelineanalyzeragent.py

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
class PipelineInput(BaseModel):
    stage: str

# ========== Tool ==========
@function_tool
def analyze_pipeline(stage: str) -> dict:
    """
    Simulates lead pipeline analysis based on the stage.
    """
    try:
        data = {
            "awareness": {"leads": 1200, "conversion_rate": "5%", "next_action": "Increase content marketing"},
            "consideration": {"leads": 800, "conversion_rate": "10%", "next_action": "Launch remarketing campaign"},
            "decision": {"leads": 400, "conversion_rate": "25%", "next_action": "Engage with high-value offers"}
        }
        return data.get(stage.lower(), {})
    except Exception as e:
        return {"error": str(e)}

# ========== Agent ==========
pipeline_agent = Agent(
    name="LeadPipelineAnalyzerAgent",
    instructions=(
        "You're a B2B marketing assistant. Analyze the lead pipeline at various funnel stages.\n"
        "Always use analyze_pipeline. If no data is found, reason using the LLM and provide suggestions."
    ),
    tools=[analyze_pipeline],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📊 Lead Pipeline Analyzer Agent Ready!")
        while True:
            user_input = input("Enter pipeline stage (awareness/consideration/decision) or 'exit': ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            input_data = [{"role": "user", "content": f"Analyze the {user_input} stage of the lead pipeline"}]
            result = await Runner.run(pipeline_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_pipeline_agent(stage: str) -> str:
    if not stage:
        stage = "awareness"  # Default fallback
    input_data = [{"role": "user", "content": f"Analyze the {stage} stage of the lead pipeline"}]
    try:
        result = await Runner.run(pipeline_agent, input_data)
        return result.final_output or "⚠️ No pipeline data found."
    except Exception as e:
        return f"⚠️ Lead pipeline agent failed: {str(e)}"

# ========== Sample Automation Trigger ==========
# async def automation_demo():
#     print(await run_pipeline_agent("decision"))
# asyncio.run(automation_demo())
#======================
def get_lead_pipeline_analyzer_tool():
    """
    Exposes LeadPipelineAnalyzerAgent as a tool for orchestrators.
    """
    return pipeline_agent.as_tool(
        tool_name="lead_pipeline_analyzer_agent",
        tool_description="Analyzes lead pipeline stages (awareness, consideration, decision) and suggests actions."
    )

