import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

# ========== Configuration ==================================
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

class CTAInput(BaseModel):
    content: str
    icp_stage: str

# ========== Tool ==========

@function_tool
def insert_cta(content: str, icp_stage: str) -> str:
    """
    Adds a contextual call-to-action (CTA) at the end of the content based on ICP stage.
    """
    icp_ctas = {
        "awareness": "📢 Learn more about our solutions [here](https://example.com/learn-more).",
        "consideration": "💡 Compare our offerings and see how we fit your needs [here](https://example.com/compare).",
        "decision": "🚀 Get started with a free trial [here](https://example.com/start-now)."
    }

    cta = icp_ctas.get(icp_stage.lower(), "👉 Contact us today for a custom solution!")
    return f"{content.strip()}\n\n<hr>\n<p><strong>{cta}</strong></p>"

# ========== Agent ==========

cta_inserter_agent = Agent(
    name="CTAInserterAgent",
    instructions="""
You're a CTA Insertion Assistant.

🎯 Your job is to:
- Analyze the provided content and ICP stage.
- Insert the most relevant CTA at the end.
- Output clean formatted content with the CTA.

✅ Always use the `insert_cta` tool.
""",
    tools=[insert_cta],
    model=model
)

# ========== CLI Mode ==========

if __name__ == "__main__":
    async def main():
        print("📢 CTA Inserter Agent Ready!")
        while True:
            content = input("📝 Paste your content (or 'exit'): ").strip()
            if content.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            stage = input("🎯 Enter ICP stage (awareness / consideration / decision): ").strip()
            input_data = [{"role": "user", "content": f"Add CTA for ICP stage '{stage}':\n\n{content}"}]
            result = await Runner.run(cta_inserter_agent, input_data)
            print("\n🔗 CTA-Enhanced Output:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========

async def run_cta_inserter_agent(content: str, icp_stage: str) -> str:
    """
    Automation runner for CTAInserterAgent.
    Call this from orchestrator: await run_cta_inserter_agent(content, "decision")
    """
    if not content:
        content = "Default content goes here."
    if not icp_stage:
        icp_stage = "awareness"

    input_data = [{"role": "user", "content": f"Add CTA for ICP stage '{icp_stage}':\n\n{content}"}]
    result = await Runner.run(cta_inserter_agent, input_data)
    return result.final_output

# ========== Export as Tool ==========

def get_cta_inserter_agent_tool():
    """
    Exported CTAInserterAgent as a tool for orchestrator or other agents.
    """
    return cta_inserter_agent.as_tool(
        tool_name="cta_inserter",
        tool_description="Add an ICP-specific CTA at the end of content"
    )
