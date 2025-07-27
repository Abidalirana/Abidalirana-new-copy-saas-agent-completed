import os
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel

# ===== Load .env and Config =====
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

# ===== Schema for WordPress Input =====
class WordPressInput(BaseModel):
    wordpress_url: str
    username: str
    application_password: str
    title: str
    content: str
    status: str = "publish"

# ===== Tool to Post to WordPress =====
@function_tool
def post_to_wordpress(wordpress_url: str, username: str, application_password: str,
                      title: str, content: str, status: str = "publish") -> str:
    try:
        endpoint = f"{wordpress_url}/wp-json/wp/v2/posts"
        auth = (username, application_password)
        data = {
            "title": title,
            "content": content,
            "status": status
        }

        response = requests.post(endpoint, json=data, auth=auth)
        response.raise_for_status()
        post_url = response.json().get("link", "[No URL]")
        return f"✅ WordPress post published!\n🔗 {post_url}"
    except Exception as e:
        return f"❌ Failed to publish: {str(e)}"

# ===== Agent Setup =====
wordpress_publisher_agent = Agent(
    name="WordPressPublisherAgent",
    instructions="""
You are the WordPress Publisher Agent. You post blogs to WordPress using their API.

✅ Required: wordpress_url, username, application_password, title, content
🛠️ Always use post_to_wordpress tool to publish.
📌 Always confirm post success and show the blog link.
🆘 If anything fails, return a clear error message.
""",
    tools=[post_to_wordpress],
    model=model
)

# ===== Automation Function (for Orchestrator) =====
async def run_wordpress_publisher_agent(post_payload: dict) -> str:
    """
    Run the WordPress agent using payload containing:
    - wordpress_url, username, application_password, title, content, (optional: status)
    """
    required_keys = ['wordpress_url', 'username', 'application_password', 'title', 'content']
    for key in required_keys:
        if key not in post_payload:
            return f"⚠️ Missing required field: {key}"

    prompt = (
        f"Post to WordPress titled '{post_payload['title']}' as '{post_payload.get('status', 'publish')}'.\n"
        f"Content: {post_payload['content']}\n"
        f"URL: {post_payload['wordpress_url']}\nUser: {post_payload['username']}"
    )

    result = await Runner.run(
        wordpress_publisher_agent,
        [{"role": "user", "content": prompt}],
        tool_input=post_payload
    )
    return result.final_output

# ===== Tool Export for Agent-as-Tool usage =====
def get_wordpress_agent_tool():
    return wordpress_publisher_agent.as_tool(
        tool_name="wordpress_publisher",
        tool_description="Publishes a blog post to a WordPress site using its REST API."
    )

# ===== CLI Manual Test =====
if __name__ == "__main__":
    import asyncio

    print("\n🧪 Manual Test: Enter WordPress post info below")
    post_data = {
        "wordpress_url": input("🌐 WordPress URL: "),
        "username": input("👤 Username: "),
        "application_password": input("🔑 Application Password: "),
        "title": input("📝 Post Title: "),
        "content": input("📄 Post Content: "),
        "status": input("📌 Status (publish/draft): ") or "publish"
    }

    print("\n⏳ Posting to WordPress...")
    output = asyncio.run(run_wordpress_publisher_agent(post_data))
    print(f"\n🔚 Agent Output:\n{output}")
