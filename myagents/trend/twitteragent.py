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
class TwitterSearchInput(BaseModel):
    query: str

    def query(self):
        return [{"role": "user", "content": f"What is trending on Twitter about {self.query}?"}]

# ========== Aliases & Utilities ==========

POPULAR_TOPICS = ["technology", "startups", "ai", "politics", "news", "sports", "crypto", "education", "global"]

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

def _fetch_twitter_trends(topic: str):
    data = {
        "technology": [
            "Apple is working on AI features for iPhone 16.",
            "Google DeepMind releases new open-source model.",
            "Tesla shares spike after new product leak.",
            "Meta’s Threads gains more traction vs. Twitter.",
            "ChatGPT gets plugin upgrades for devs."
        ],
        "sports": [
            "Olympics 2025 prep begins in Paris.",
            "Ronaldo scores a record-breaking goal.",
            "India vs Pakistan clash breaks viewership records.",
            "FIFA considering rule changes.",
            "NBA trade rumors heat up."
        ],
        "ai": [
            "ChatGPT-5 beta rumored to release in September.",
            "Claude 3 outperforms GPT in new benchmarks.",
            "Open-source LLMs closing in on commercial models.",
            "Governments debating AI regulation frameworks.",
            "OpenAI launches AI music generation tool."
        ],
        "global": [
            "Climate crisis dominates UN talks.",
            "Elon Musk makes surprise trip to China.",
            "Crypto markets see weekend rally.",
            "Hollywood strikes finally come to an end.",
            "New tech unicorns emerge in Southeast Asia."
        ]
    }
    return data.get(topic.lower(), [])

def llm_summary_about(topic: str) -> str:
    return f"{topic.title()} is currently not trending, but it’s a topic of ongoing interest in technology and media conversations."

# ========== Tools ==========
@function_tool
def get_twitter_trending(topic: str) -> list[str]:
    """
    This tool fetches realistic trending data for a given topic on Twitter.
    """
    topic = _normalize_topic(topic)
    trends = _fetch_twitter_trends(topic)

    if trends:
        return [f"🔹 {trend}" for trend in trends]
    else:
        summary = llm_summary_about(topic)
        fallback = (
            f"⚠️ No live Twitter trends found for '{topic}'.\n"
            "But here's what Twitter is talking about more broadly:\n"
            "- AI tools like ChatGPT are trending.\n"
            "- Political debates around elections.\n"
            "- Crypto updates with Bitcoin price fluctuations.\n"
            "- Climate change and protests.\n"
            "- New gadget launches from major tech companies.\n\n"
            f"🧠 Quick insight on '{topic}':\n{summary}"
        )
        return [fallback]

# ========== Agent ==========
twitter_agent = Agent(
    name="TwitterTrendAgent",
    instructions=(
        "You're an expert Twitter trend assistant. Your job is to find and explain the top trending topics on Twitter.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Always use the `get_twitter_trending` tool to fetch trends.\n"
        "- If the user gives a vague query like 'what’s trending', assume topic = 'global'.\n"
        "- Normalize topic names using synonyms or closest matches.\n"
        "- Always handle missing or empty topics gracefully.\n"
        "- If no trending data is found, provide a helpful fallback based on general Twitter activity.\n\n"
        "💡 Example Queries:\n"
        "- 'What’s hot in tech today?'\n"
        "- 'Tell me the latest trends about politics'\n"
        "- 'Give trending data for AI'\n"
        "- 'Trending topics on Twitter?'\n\n"
        "✅ Response Format:\n"
        "- Title: 'Top 5 trends about [normalized_topic]:'\n"
        "- Use bullet points ✅\n"
        "- Make each bullet a smart summary of the topic, like a tweet or news blurb.\n"
        "- Avoid robotic numbering (no 'trend 1', 'trend 2')\n\n"
        "⚠️ Fallback Instructions:\n"
        "- If no trends are available, fallback with:\n"
        "  'Twitter is buzzing with discussions around Artificial Intelligence, especially tools like ChatGPT and Claude 3. Sports controversies and political updates are also trending globally.'"
    ),
    tools=[get_twitter_trending],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":

    async def main():
        print("🔍 Twitter Trend Agent Ready!")
        while True:
            user_input = input("🔎 Enter a topic (or type 'exit'): ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            vague_keywords = ["trending", "what's hot", "buzzing", "latest", "give me twitter updates", "suggest", "anything trending"]
            if not any(word in user_input.lower() for word in POPULAR_TOPICS):
                if any(key in user_input.lower() for key in vague_keywords):
                    user_input = "global"

            input_data = [{"role": "user", "content": f"What is trending on Twitter about {user_input}?"}]
            result = await Runner.run(twitter_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_twitter_agent(query: str) -> str:
    if not query or query.strip().lower() in ["trending", ""]:
        query = "global"

    input_data = [{"role": "user", "content": f"What is trending on Twitter about {query}?"}]
    result = await Runner.run(twitter_agent, input_data)
    return result.final_output

# 🧪 Optional: Test without CLI
# async def automation_demo():
#     response = await run_twitter_agent("startups")
#     print("🤖 Automation Output:\n", response)

# asyncio.run(automation_demo())

# ========== Export as Tool ==========
def get_twitter_agent_tool():
    """
    Exported agent tool to be used inside orchestrator.
    """
    return twitter_agent.as_tool(
        tool_name="twitter_trends",
        tool_description="Get trending topics on Twitter for a given topic or keyword"
    )
