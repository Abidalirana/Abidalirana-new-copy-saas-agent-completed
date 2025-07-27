# ✅ Starting Agent 1: engager_scraper_agent.py

# File: engager_scraper_agent.py
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
class LinkedInPostInput(BaseModel):
    post_url: str

    def query(self):
        return [{"role": "user", "content": f"Scrape all engagers on this LinkedIn post: {self.post_url}"}]

# ========== Tool ==========
@function_tool
def scrape_linkedin_engagers(post_url: str) -> list[str]:
    """
    Tool to simulate scraping of engagers from a LinkedIn post.
    """
    if "linkedin.com" not in post_url:
        return ["❌ Invalid LinkedIn URL."]

    # Simulated data
    engagers = [
        "👤 John Doe - Liked",
        "💬 Jane Smith - Commented",
        "🔁 Robert Johnson - Shared"
    ]
    return engagers

# ========== Agent ==========
engager_scraper_agent = Agent(
    name="EngagerScraperAgent",
    instructions=(
        "You're a LinkedIn engager scraping agent. Your job is to fetch the list of users who interacted with a given LinkedIn post.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Use the `scrape_linkedin_engagers` tool.\n"
        "- If the post URL is invalid, respond with a helpful error.\n"
        "- Summarize the type of engagement.\n"
        "\n✅ Response Format:\n"
        "- Bullet list of engagers (name and interaction type)."
    ),
    tools=[scrape_linkedin_engagers],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🔍 Engager Scraper Agent Ready!")
        while True:
            user_input = input("🔗 Enter LinkedIn Post URL (or 'exit'): ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            input_data = [{"role": "user", "content": f"Scrape all engagers on this LinkedIn post: {user_input}"}]

            try:
                result = await Runner.run(engager_scraper_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_engager_scraper_agent(post_url: str) -> str:
    if not post_url:
        return "❌ No LinkedIn post URL provided."

    input_data = [{"role": "user", "content": f"Scrape all engagers on this LinkedIn post: {post_url}"}]
    try:
        result = await Runner.run(engager_scraper_agent, input_data)
        if not result.final_output:
            return "❌ No engagers found."
        return result.final_output
    except Exception as e:
        return f"⚠️ Failed to fetch engagers: {str(e)}"

# 🧪 Uncomment below to simulate
# async def test():
#     response = await run_engager_scraper_agent("https://linkedin.com/posts/sample")
#     print(response)
# asyncio.run(test())
#=========================
# ========== Tool Export ========== #
def get_engager_scraper_tool():
    return engager_scraper_agent.as_tool(
        tool_name="scrape_linkedin_engagers",
        tool_description="Scrapes engagers (likers, commenters, sharers) from a LinkedIn post.",
    )

