import os
import asyncio
import difflib
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
class IndieSearchInput(BaseModel):
    query: str

    def to_prompt(self):
        return [{"role": "user", "content": f"What’s trending on Indie Hackers about {self.query}?"}]

# ========== Aliases & Utilities ==========
POPULAR_TOPICS = [
    "bootstrapping", "saas", "indie hackers", "nocode", "side projects",
    "marketing", "growth", "startup", "revenue", "founders"
]

ALIASES = {
    "no-code": "nocode",
    "startups": "startup",
    "hackers": "indie hackers",
    "build": "side projects"
}

def _normalize_topic(topic: str) -> str:
    topic = topic.strip().lower()
    topic = ALIASES.get(topic, topic)
    match = difflib.get_close_matches(topic, POPULAR_TOPICS, n=1, cutoff=0.65)
    return match[0] if match else topic

def _fetch_indie_trends(topic: str):
    data = {
        "bootstrapping": [
            "How I bootstrapped my SaaS to $10k MRR",
            "Bootstrapping tips for solo founders",
            "When to hire as a bootstrapper?"
        ],
        "nocode": [
            "Top No-Code tools in 2025",
            "I built a SaaS with zero code",
            "Nocode vs custom dev: What's better?"
        ],
        "marketing": [
            "How I got 1000 users from Reddit",
            "Free tools to analyze your growth",
            "Cold email templates that work"
        ]
    }
    return data.get(topic.lower(), [])

def llm_summary_about(topic: str) -> str:
    return f"While '{topic}' isn't trending right now, it's a popular Indie Hackers topic discussed in many bootstrapping and growth threads."

# ========== Tools ==========
@function_tool
def get_indie_trending(topic: str) -> list[str]:
    """
    Retrieves current trending discussions from Indie Hackers about a specific topic.
    """
    topic = _normalize_topic(topic)
    trends = _fetch_indie_trends(topic)

    if trends:
        return [f"🧠 {trend}" for trend in trends]
    else:
        summary = llm_summary_about(topic)
        fallback = (
            f"⚠️ No live Indie Hackers trends found for '{topic}'.\n"
            "But here’s what’s generally discussed:\n"
            "- Launching without funding\n"
            "- Building with no-code tools\n"
            "- Finding first 100 customers\n\n"
            f"💡 Insight: {summary}"
        )
        return [fallback]

# ========== Agent ==========
indie_agent = Agent(
    name="IndieHackerTrendAgent",
    instructions=(
        "You’re an Indie Hackers insights expert. Help users discover top discussions.\n\n"
        "🧠 Smart Instructions:\n"
        "- Always use `get_indie_trending` to get trends.\n"
        "- Normalize unclear terms using known topic list.\n"
        "- If nothing found, offer helpful fallback with insight.\n"
        "- Respond like a solo founder sharing advice in a community.\n\n"
        "💬 Sample Queries:\n"
        "- 'What's trending in no-code?'\n"
        "- 'Bootstrapping tips?'\n"
        "- 'Anything on indie hacker growth?'\n\n"
        "✅ Format:\n"
        "- Title: 'Here’s what’s trending on Indie Hackers about [topic]:'\n"
        "- Use engaging bullet points\n"
        "- Add smart summary if needed"
    ),
    tools=[get_indie_trending],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":

    async def main():
        print("🚀 Indie Hacker Trend Agent Ready!")
        while True:
            user_input = input("💬 Enter a topic (or type 'exit'): ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting. Keep hustling!")
                break

            vague_keywords = ["trending", "buzzing", "hot", "new", "indie"]
            if not any(word in user_input.lower() for word in POPULAR_TOPICS):
                if any(key in user_input.lower() for key in vague_keywords):
                    user_input = "bootstrapping"

            input_data = [{"role": "user", "content": f"What is trending on Indie Hackers about {user_input}?"}]
            result = await Runner.run(indie_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation ==========
async def run_indie_agent(topic: str = "bootstrapping") -> str:
    input_data = [{"role": "user", "content": f"What is trending on Indie Hackers about {topic}?"}]
    result = await Runner.run(indie_agent, input_data)
    return result.final_output

def get_indie_agent_tool():
    return indie_agent.as_tool(
        tool_name="indie_trends",
        tool_description="Get trending Indie Hackers discussions for a given topic like bootstrapping, nocode, or marketing"
    )
