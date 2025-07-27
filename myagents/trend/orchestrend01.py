import sys
import os

# ✅ Add the root directory (2 levels up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))




import os
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
from myagents.trend.twitteragent import get_twitter_agent_tool
from myagents.trend.redditagent import get_reddit_agent_tool
from myagents.trend.quoratrendagent import get_quora_agent_tool
from myagents.trend.linkedintrendagent import get_linkedin_agent_tool
from myagents.trend.indiehackertrendagent import get_indie_agent_tool

# ========== Load Tools ========== #
twitter_tool = get_twitter_agent_tool()
reddit_tool = get_reddit_agent_tool()
quora_tool = get_quora_agent_tool()
linkedin_tool = get_linkedin_agent_tool()
indie_tool = get_indie_agent_tool()

# ========== Define Orchestrator Agent ========== #
trend_orchestrator = Agent(
    name="TrendOrchestratorAgent",
    instructions="""
You're a trend aggregation agent. Your job is to gather trending topics from Twitter, Reddit, Quora, LinkedIn, and Indie Hackers.

🧠 Rules:
- Always use all tools provided.
- Normalize vague input to 'global'.
- Combine the results into a concise summary.
- Provide bullet-point summaries for each platform.
""",
    tools=[
        twitter_tool,
        reddit_tool,
        quora_tool,
        linkedin_tool,
        indie_tool
    ],
    model=model
)

# ========== Export as Tool ========== #
def get_trend_orchestrator_tool():
    return trend_orchestrator.as_tool(
        tool_name="trend_orchestrator",
        tool_description="Aggregates and summarizes trending topics across Twitter, Reddit, Quora, LinkedIn, and Indie Hackers"
    )

# ========== Optional CLI Runner ========== #
async def run_orchestrator():
    tool_choices = {
        "1": twitter_tool,
        "2": reddit_tool,
        "3": quora_tool,
        "4": linkedin_tool,
        "5": indie_tool
    }

    tool_names = {
        "1": "Twitter",
        "2": "Reddit",
        "3": "Quora",
        "4": "LinkedIn",
        "5": "IndieHackers"
    }

    print("\n🛠️ Select which platforms to include:")
    print("1. Twitter\n2. Reddit\n3. Quora\n4. LinkedIn\n5. IndieHackers")
    selected = input("➡️ Enter numbers separated by comma (e.g., 1,2,5 or press Enter for all): ").strip()

    if selected:
        selected_indices = [s.strip() for s in selected.split(",") if s.strip() in tool_choices]
        selected_tools = [tool_choices[i] for i in selected_indices]
        selected_names = [tool_names[i] for i in selected_indices]
    else:
        selected_tools = [twitter_tool, reddit_tool, quora_tool, linkedin_tool, indie_tool]
        selected_names = list(tool_names.values())

    print(f"✅ You selected: {', '.join(selected_names)}")

    # Create dynamic orchestrator agent with selected tools
    dynamic_trend_orchestrator = Agent(
        name="TrendOrchestratorAgent",
        instructions=trend_orchestrator.instructions,
        tools=selected_tools,
        model=model
    )

    while True:
        topic = input("\n🔎 Enter a topic (or type 'exit' to quit): ").strip()
        if topic.lower() in ["exit", "quit"]:
            print("👋 Exiting. Goodbye!")
            break

        if not topic:
            topic = "global"

        try:
            result = await Runner.run(dynamic_trend_orchestrator, topic)
            print("\n🧠 Final Aggregated Output:\n")
            print(result.final_output)
        except Exception as e:
            print(f"❌ An error occurred while running the orchestrator: {e}")


if __name__ == "__main__":
    asyncio.run(run_orchestrator())
