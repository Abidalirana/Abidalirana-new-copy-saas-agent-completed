import os
import asyncio
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

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
class LinkedInInput(BaseModel):
    access_token: str
    author_urn: str  # Example: "urn:li:person:abc123xyz"
    post_text: str

# ========== Tool ==========
@function_tool
def post_to_linkedin(data: LinkedInInput) -> str:
    """
    Publishes a post on LinkedIn using their API.
    """
    try:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {data.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        payload = {
            "author": data.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": data.post_text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"✅ LinkedIn post published! Post URN: {response.json().get('id', '[no id]')}"
    except Exception as e:
        return f"❌ Failed to publish on LinkedIn: {str(e)}"

# ========== Agent ==========
linkedin_poster_agent = Agent(
    name="LinkedInPosterAgent",
    instructions="""
You are the LinkedIn Poster Agent. Your job is to publish posts to LinkedIn via API.

✅ Input fields: `access_token`, `author_urn`, `post_text`
🛠️ Use `post_to_linkedin` tool to post
🔁 Return success message or clear error
""",
    tools=[post_to_linkedin],
    model=model
)

# ========== CLI Runner ==========
if __name__ == "__main__":
    async def main():
        print("🔗 LinkedIn Poster Agent Ready!")
        while True:
            text = input("✍️ Enter post text (or 'exit'): ").strip()
            if text.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            token = input("🔑 Access Token: ").strip()
            author_urn = input("👤 Author URN (e.g., urn:li:person:abc): ").strip()

            result = await Runner.run(
                linkedin_poster_agent,
                [{"role": "user", "content": f"Post to LinkedIn as {author_urn}. Content: {text}"}],
                tool_input={
                    "access_token": token,
                    "author_urn": author_urn,
                    "post_text": text
                }
            )
            print("\n📢 Result:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation ==========
async def run_linkedin_poster_agent(access_token: str, author_urn: str, post_text: str) -> str:
    """
    Automation entry point for orchestrator.
    """
    if not access_token or not author_urn or not post_text:
        return "⚠️ Missing required LinkedIn fields."

    result = await Runner.run(
        linkedin_poster_agent,
        [{"role": "user", "content": f"Post to LinkedIn as {author_urn}. Content: {post_text}"}],
        tool_input={
            "access_token": access_token,
            "author_urn": author_urn,
            "post_text": post_text
        }
    )
    return result.final_output

# ========== Tool Export ==========
def get_linkedin_agent_tool():
    return linkedin_poster_agent.as_tool(
        tool_name="linkedin_poster",
        tool_description="Publishes a post to LinkedIn using the official API"
    )
