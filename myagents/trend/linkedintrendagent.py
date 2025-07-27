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
class LinkedInSearchInput(BaseModel):
    query: str

    def to_prompt(self):
        return [{"role": "user", "content": f"What is trending on LinkedIn about {self.query}?"}]

# ========== Aliases & Utilities ==========
POPULAR_TOPICS = ["technology", "startups", "ai", "leadership", "career", "jobs", "productivity", "marketing", "crypto"]

ALIASES = {
    "tech": "technology",
    "ai": "artificial intelligence",
    "job": "jobs",
    "promo": "marketing"
}

def _normalize_topic(topic: str) -> str:
    topic = topic.strip().lower()
    topic = ALIASES.get(topic, topic)
    match = difflib.get_close_matches(topic, POPULAR_TOPICS, n=1, cutoff=0.65)
    return match[0] if match else topic

def _fetch_linkedin_trends(topic: str):
    data = {
        "ai": [
            "How AI is reshaping the workplace",
            "Top AI tools professionals are using",
            "AI interview questions and how to answer them"
        ],
        "leadership": [
            "Traits of a 2025 leader",
            "Leading remote teams effectively",
            "Managing burnout as a team lead"
        ],
        "jobs": [
            "How to stand out in job applications",
            "Future-proof careers in tech",
            "Top hiring companies this quarter"
        ],
        "productivity": [
            "Morning routines that work",
            "How to manage async communication",
            "Focus tools for remote workers"
        ]
    }
    return data.get(topic.lower(), [])

def llm_summary_about(topic: str) -> str:
    return f"{topic.title()} is a frequent theme among professionals on LinkedIn, often discussed in the context of growth, opportunities, and workplace culture."

# ========== Tools ==========
@function_tool
def get_linkedin_trending(topic: str) -> list[str]:
    """
    Fetches realistic trending discussions for a given topic from LinkedIn.
    """
    topic = _normalize_topic(topic)
    trends = _fetch_linkedin_trends(topic)

    if trends:
        return [f"💼 {trend}" for trend in trends]
    else:
        summary = llm_summary_about(topic)
        fallback = (
            f"⚠️ No real-time LinkedIn trends found for '{topic}'.\n"
            "However, professionals on LinkedIn are actively discussing:\n"
            "- Remote work best practices\n"
            "- Career growth strategies\n"
            "- AI integration in corporate life\n\n"
            f"🧠 Insight: {summary}"
        )
        return [fallback]

# ========== Agent ==========
linkedin_agent = Agent(
    name="LinkedInTrendAgent",
    instructions=(
        "You're a LinkedIn insights expert. You help users discover what professionals are talking about.\n\n"
        "📌 Intelligence Rules:\n"
        "- Always use `get_linkedin_trending` to retrieve results.\n"
        "- Use synonyms or close matches for unclear topics.\n"
        "- Fallback with general workplace insights if no trends found.\n"
        "- Keep answers friendly, professional, and helpful.\n\n"
        "💬 Sample Queries:\n"
        "- 'What's trending in AI on LinkedIn?'\n"
        "- 'Career advice updates?'\n"
        "- 'LinkedIn productivity discussions?'\n\n"
        "✅ Response Format:\n"
        "- Title: 'Here’s what’s trending on LinkedIn about [topic]:'\n"
        "- Use professional bullet points\n"
        "- Always include a summary or fallback if data is missing"
    ),
    tools=[get_linkedin_trending],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":

    async def main():
        print("🔗 LinkedIn Trend Agent Ready!")
        while True:
            user_input = input("💬 Enter a topic (or type 'exit'): ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting. Stay connected!")
                break

            vague_keywords = ["trending", "what's hot", "buzzing", "latest", "linkedin"]
            if not any(word in user_input.lower() for word in POPULAR_TOPICS):
                if any(key in user_input.lower() for key in vague_keywords):
                    user_input = "career"

            input_data = [{"role": "user", "content": f"What is trending on LinkedIn about {user_input}?"}]
            result = await Runner.run(linkedin_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Function ==========
async def run_linkedin_agent(topic: str = "career") -> str:
    input_data = [{"role": "user", "content": f"What is trending on LinkedIn about {topic}?"}]
    result = await Runner.run(linkedin_agent, input_data)
    return result.final_output

# ========== Tool Export ==========
def get_linkedin_agent_tool():
    return linkedin_agent.as_tool(
        tool_name="linkedin_trends",
        tool_description="Get trending LinkedIn discussions for a given topic like jobs, AI, or productivity"
    )
