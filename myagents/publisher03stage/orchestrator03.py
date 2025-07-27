import sys
import os

# ✅ Add the root directory (2 levels up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel

# ========== Load Env & Config ========== #
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

# ========== Import Publisher Tools ========== #
from myagents.publisher03stage.brevopublisheragent import get_brevo_agent_tool
from myagents.publisher03stage.contentqueuemanager import get_contentqueue_agent_tool
from myagents.publisher03stage.linkedInposteragent import get_linkedin_agent_tool
from myagents.publisher03stage.scheduleragent import get_scheduler_agent_tool
from myagents.publisher03stage.wordpresspublisheragent import get_wordpress_agent_tool

# ========== Load Tools ========== #
brevo_tool = get_brevo_agent_tool()
queue_tool = get_contentqueue_agent_tool()
linkedin_tool = get_linkedin_agent_tool()
scheduler_tool = get_scheduler_agent_tool()
wordpress_tool = get_wordpress_agent_tool()

# ========== Define Publisher Orchestrator Agent ========== #
publisher_orchestrator = Agent(
    name="PublisherOrchestratorAgent",
    instructions="""
You are the Publisher Orchestrator Agent. You manage and coordinate publishing content to various platforms.

🧠 Rules:
- Use the content queue to get drafts or inputs.
- Use LinkedIn, Brevo, WordPress tools to publish.
- Use the scheduler if delayed publishing is requested.
- Validate inputs before dispatching to platform agents.
- Reply with clear confirmation of where and what was posted.
""",
    tools=[
        queue_tool,
        linkedin_tool,
        brevo_tool,
        wordpress_tool,
        scheduler_tool
    ],
    model=model
)

# ========== Export as Tool (Optional) ========== #
def get_publisher_orchestrator_tool():
    return publisher_orchestrator.as_tool(
        tool_name="publisher_orchestrator",
        tool_description="Coordinates publishing to LinkedIn, Brevo, WordPress, and handles scheduling."
    )

# ========== Optional CLI Runner ========== #
async def run_orchestrator():
    tool_choices = {
        "1": queue_tool,
        "2": linkedin_tool,
        "3": brevo_tool,
        "4": wordpress_tool,
        "5": scheduler_tool
    }

    tool_names = {
        "1": "ContentQueue",
        "2": "LinkedIn",
        "3": "Brevo",
        "4": "WordPress",
        "5": "Scheduler"
    }

    print("\n📢 Select which agents to activate:")
    print("1. ContentQueue\n2. LinkedIn\n3. Brevo\n4. WordPress\n5. Scheduler")
    selected = input("➡️ Enter numbers separated by comma (or press Enter for all): ").strip()

    if selected:
        selected_indices = [s.strip() for s in selected.split(",") if s.strip() in tool_choices]
        selected_tools = [tool_choices[i] for i in selected_indices]
        selected_names = [tool_names[i] for i in selected_indices]
    else:
        selected_tools = list(tool_choices.values())
        selected_names = list(tool_names.values())

    print(f"✅ Using: {', '.join(selected_names)}")

    # Create dynamic orchestrator with selected tools
    dynamic_orchestrator = Agent(
        name="PublisherOrchestratorAgent",
        instructions=publisher_orchestrator.instructions,
        tools=selected_tools,
        model=model
    )

    while True:
        content = input("\n✍️  Enter content to publish (or type 'exit'): ").strip()
        if content.lower() in ["exit", "quit"]:
            print("👋 Exiting Publisher Orchestrator.")
            break

        try:
            result = await Runner.run(dynamic_orchestrator, content)
            print("\n✅ Final Result:\n")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error while running orchestrator: {e}")

if __name__ == "__main__":
    asyncio.run(run_orchestrator())
