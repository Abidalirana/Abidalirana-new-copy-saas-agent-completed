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
class QuoraSearchInput(BaseModel):
    query: str

    def to_prompt(self):
        return [{"role": "user", "content": f"What is trending on Quora about {self.query}?"}]

# ========== Aliases & Utilities ==========
POPULAR_TOPICS = ["technology", "startups", "ai", "politics", "news", "sports", "crypto", "education", "health"]

ALIASES = {
    "tech": "technology",
    "ai": "artificial intelligence",
    "edu": "education",
    "crypto": "cryptocurrency"
}

def _normalize_topic(topic: str) -> str:
    topic = topic.strip().lower()
    topic = ALIASES.get(topic, topic)
    match = difflib.get_close_matches(topic, POPULAR_TOPICS, n=1, cutoff=0.65)
    return match[0] if match else topic

def _fetch_quora_trends(topic: str):
    data = {
        "technology": [
            "What is the future of AI and humanity?",
            "Which are the top programming languages in 2025?",
            "How are tech startups surviving economic slowdowns?"
        ],
        "education": [
            "Are degrees still relevant in 2025?",
            "Which online courses are best for self-learning?",
            "How to stay productive while studying from home?"
        ],
        "health": [
            "What are the side effects of long-term screen time?",
            "How to boost immunity naturally?",
            "What is mental health hygiene and why is it important?"
        ]
    }
    return data.get(topic.lower(), [])

def llm_summary_about(topic: str) -> str:
    return f"While {topic} isn't currently trending, it's a topic of ongoing discussion in the Quora community."

# ========== Tool ==========
@function_tool
def get_quora_trending(topic: str) -> list[str]:
    """
    This tool fetches realistic trending questions from Quora for a given topic.
    """
    topic = _normalize_topic(topic)
    trends = _fetch_quora_trends(topic)

    if trends:
        return [f"❓ {trend}" for trend in trends]
    else:
        summary = llm_summary_about(topic)
        fallback = (
            f"⚠️ No live Quora trends found for '{topic}'.\n"
            "But here's what people generally ask on Quora:\n"
            "- Life advice and productivity tips\n"
            "- Education and online courses\n"
            "- Health and self-improvement\n"
            f"\n🧠 Insight: {summary}"
        )
        return [fallback]

# ========== Agent ==========
quora_agent = Agent(
    name="QuoraTrendAgent",
    instructions=(
        "You're an intelligent Quora trend expert. You retrieve the most relevant trending topics from Quora.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Always use the `get_quora_trending` tool.\n"
        "- Normalize vague inputs like 'buzzing' to a default topic = 'education'.\n"
        "- If the topic is unknown, give a fallback response with context.\n"
        "- Respond like a human who is helpful and a bit curious.\n\n"
        "💡 Example Queries:\n"
        "- 'What's popular in health topics?'\n"
        "- 'Any trending questions on tech?'\n"
        "- 'Quora education topics?'\n\n"
        "✅ Response Format:\n"
        "- Title: 'Top trending questions on [topic]:'\n"
        "- Use bullets for clarity\n"
        "- Fallback when needed should be smart, not robotic."
    ),
    tools=[get_quora_trending],
    model=model
)

# ========== Runner for CLI ==========
if __name__ == "__main__":

    async def main():
        print("🔍 Quora Trend Agent Ready!")
        while True:
            user_input = input("🔎 Enter a topic (or type 'exit'): ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            vague_keywords = ["trending", "what's hot", "buzzing", "latest", "quora"]
            if not any(word in user_input.lower() for word in POPULAR_TOPICS):
                if any(key in user_input.lower() for key in vague_keywords):
                    user_input = "education"

            input_data = [{"role": "user", "content": f"What is trending on Quora about {user_input}?"}]
            result = await Runner.run(quora_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry ==========
async def run_quora_agent(topic: str = "education") -> str:
    input_data = [{"role": "user", "content": f"What is trending on Quora about {topic}?"}]
    result = await Runner.run(quora_agent, input_data)
    return result.final_output

# ========== Tool Export ==========
def get_quora_agent_tool():
    return quora_agent.as_tool(
        tool_name="quora_trends",
        tool_description="Get trending questions on Quora for a given topic like technology or education"
    )
