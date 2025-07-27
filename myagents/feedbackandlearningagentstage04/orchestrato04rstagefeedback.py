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

# ========== Import Tool Loaders ========== #
from myagents.feedbackandlearningagentstage04.contentperformanceagent import get_content_performance_tool
from myagents.feedbackandlearningagentstage04.contentrefineragent import run_refiner_agent
from myagents.feedbackandlearningagentstage04.engagementmonitoragent import get_engagement_monitor_tool
from myagents.feedbackandlearningagentstage04.insightextractoragent import get_insight_extractor_tool
from myagents.feedbackandlearningagentstage04.postmortemagent import get_postmortem_agent_tool

# ========== Load Tools (async-safe) ========== #
async def load_tools():
    content_tool = get_content_performance_tool()
    refiner_tool = await run_refiner_agent()  # ✅ Proper await
    engagement_tool = get_engagement_monitor_tool()
    insight_tool = get_insight_extractor_tool()
    postmortem_tool = get_postmortem_agent_tool()
    return content_tool, refiner_tool, engagement_tool, insight_tool, postmortem_tool

# ========== Export as Tool ========== #
async def get_feedback_orchestrator_tool():
    content_tool, refiner_tool, engagement_tool, insight_tool, postmortem_tool = await load_tools()

    feedback_orchestrator = Agent(
        name="FeedbackOrchestratorAgent",
        instructions="...",
        tools=[
            content_tool,
            refiner_tool,
            engagement_tool,
            insight_tool,
            postmortem_tool
        ],
        model=model
    )

    return feedback_orchestrator.as_tool(
        tool_name="feedback_orchestrator",
        tool_description="Coordinates performance, refinement, engagement, insights, and post-mortem analysis for content feedback."
    )

# ========== CLI Runner ========== #
async def run_orchestrator():
    content_tool, refiner_tool, engagement_tool, insight_tool, postmortem_tool = await load_tools()

    feedback_orchestrator = Agent(
        name="FeedbackOrchestratorAgent",
        instructions="""
You're an agent that coordinates feedback and learning agents. You can:
- Analyze content performance
- Refine and enhance content
- Monitor engagement
- Extract insights
- Summarize weekly results

🧠 Guidelines:
- Always provide actionable feedback
- Use metrics like CTR, likes, comments to guide reasoning
- Recommend improvements clearly
""",
        tools=[
            content_tool,
            refiner_tool,
            engagement_tool,
            insight_tool,
            postmortem_tool
        ],
        model=model
    )

    tool_choices = {
        "1": content_tool,
        "2": refiner_tool,
        "3": engagement_tool,
        "4": insight_tool,
        "5": postmortem_tool
    }

    tool_names = {
        "1": "ContentPerformance",
        "2": "Refiner",
        "3": "EngagementMonitor",
        "4": "InsightExtractor",
        "5": "PostMortem"
    }

    print("\n🛠️ Select which feedback agents to use:")
    print("1. ContentPerformance\n2. Refiner\n3. EngagementMonitor\n4. InsightExtractor\n5. PostMortem")
    selected = input("➡️ Enter numbers separated by comma (or press Enter for all): ").strip()

    if selected:
        selected_indices = [s.strip() for s in selected.split(",") if s.strip() in tool_choices]
        selected_tools = [tool_choices[i] for i in selected_indices]
        selected_names = [tool_names[i] for i in selected_indices]
    else:
        selected_tools = [content_tool, refiner_tool, engagement_tool, insight_tool, postmortem_tool]
        selected_names = list(tool_names.values())

    print(f"✅ You selected: {', '.join(selected_names)}")

    dynamic_orchestrator = Agent(
        name="FeedbackOrchestratorAgent",
        instructions=feedback_orchestrator.instructions,
        tools=selected_tools,
        model=model
    )

    while True:
        query = input("\n💬 Enter a feedback-related task (or type 'exit' to quit): ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting Feedback Orchestrator.")
            break

        if not query:
            continue

        try:
            result = await Runner.run(dynamic_orchestrator, query)
            print("\n🧠 Final Output:\n")
            print(result.final_output)
        except Exception as e:
            print(f"❌ Error during orchestration: {e}")

if __name__ == "__main__":
    asyncio.run(run_orchestrator())
