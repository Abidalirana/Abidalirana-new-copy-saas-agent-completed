import os
import asyncio
import requests
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
class RedditSearchInput(BaseModel):
    subreddit: str

    def to_prompt(self):
        return [{"role": "user", "content": f"What is trending on Reddit in r/{self.subreddit}?"}]

# ========== Tools ==========
@function_tool
def get_reddit_trending(subreddit: str) -> list[str]:
    """
    Get top trending posts from a specific subreddit.
    """
    if not subreddit:
        subreddit = "popular"

    headers = {"User-Agent": "reddit-trend-agent/0.1"}
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=5"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return [f"❌ Failed to fetch data. HTTP Status: {response.status_code}"]

        posts = response.json().get("data", {}).get("children", [])
        if not posts:
            return [f"😕 No trending posts found in r/{subreddit}. Try a broader subreddit."]

        return [f"🔹 {post['data']['title']}" for post in posts]

    except Exception as e:
        return [f"⚠️ Error fetching Reddit trends: {str(e)}"]

# ========== Agent ==========
reddit_agent = Agent(
    name="RedditTrendAgent",
    instructions=(
        "You're an intelligent Reddit assistant who fetches trending discussions from subreddits.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Always use the `get_reddit_trending` tool to fetch posts.\n"
        "- If the subreddit is vague or missing, default to 'popular'.\n"
        "- Explain missing results kindly and give suggestions.\n"
        "- Simulate a human tone with enthusiasm and clarity.\n\n"
        "💬 Example Inputs:\n"
        "- 'What’s hot on r/news today?'\n"
        "- 'Trending now in r/technology'\n"
        "- 'Show me top posts in r/sports'\n\n"
        "✅ Response Format:\n"
        "- Title: 'Top posts in r/[subreddit]:'\n"
        "- Use emoji bullets ✅\n"
        "- Max 5 post titles in natural tone\n\n"
        "⚠️ Fallback:\n"
        "- If subreddit has no results, respond with something like:\n"
        "  'No hot posts found in r/{subreddit}. Try another trending community like r/popular or r/worldnews.'"
    ),
    tools=[get_reddit_trending],
    model=model
)

# ========== Runner for CLI ==========
if __name__ == "__main__":

    async def main():
        print("👾 Reddit Trend Agent Ready!")
        while True:
            user_input = input("🔎 Enter subreddit (or type 'exit'): ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            if not user_input:
                user_input = "popular"

            input_data = [{"role": "user", "content": f"What is trending on Reddit in r/{user_input}?"}]
            result = await Runner.run(reddit_agent, input_data)
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry ==========

async def run_reddit_agent(subreddit: str = "popular") -> str:
    """
    Programmatic runner for RedditTrendAgent – used by orchestrator/automation.
    """
    if not subreddit or subreddit.strip() == "":
        subreddit = "popular"

    input_data = [{"role": "user", "content": f"What is trending on Reddit in r/{subreddit}?"}]
    result = await Runner.run(reddit_agent, input_data)
    return result.final_output

# ========== Agent as Tool for Orchestrator ==========
def get_reddit_agent_tool():
    return reddit_agent.as_tool(
        tool_name="reddit_trends",
        tool_description="Get trending Reddit posts from a specific subreddit like r/technology or r/news"
    )
