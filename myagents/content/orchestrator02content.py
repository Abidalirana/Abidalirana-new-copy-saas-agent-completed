import os
import sys
# Add root path so agents in the same folder can be imported properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#========================
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import (
    Agent,
    Runner,
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
)

# === Config ===
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

# === Import Tools ===
from myagents.content.blogwriteragent import get_blog_writer_agent_tool
from myagents.content.contentformatter_agent import get_content_formatter_agent_tool
from myagents.content.ctainserteragent import get_cta_inserter_agent_tool
from myagents.content.newsletterwriteragent import get_newsletter_agent_tool
from myagents.content.socialsnippetsagent import get_social_snippets_agent_tool

from myagents.content.reelsgenerationagent import get_reels_generation_tool
from myagents.content.socialmediaimagegenerationagent import get_social_media_image_tool
from myagents.content.blogsgenerationagent import get_blog_post_generator_tool
from myagents.content.Blogsimagegenerationagent import get_blog_image_generation_tool
from myagents.content.imagegenerationagent import get_image_generation_tool
from myagents.content.videogenerationagent import get_video_generation_tool

# === Load Tools ===
blog_tool = get_blog_writer_agent_tool()
formatter_tool = get_content_formatter_agent_tool()
cta_tool = get_cta_inserter_agent_tool()
newsletter_tool = get_newsletter_agent_tool()
snippets_tool = get_social_snippets_agent_tool()

reels_tool = get_reels_generation_tool()
social_image_tool = get_social_media_image_tool()
blog_ideas_tool = get_blog_post_generator_tool()
blog_image_tool = get_blog_image_generation_tool()
image_tool = get_image_generation_tool()
video_tool = get_video_generation_tool()

# === Define Orchestrator Agent ===
content_orchestrator = Agent(
    name="ContentCreationOrchestrator",
    instructions="""
You're a content creation orchestrator agent.
Your job is to generate polished content pieces from a single idea using available tools.

🧠 What to do:
- Use all tools to create full content pipeline:
    1. Generate long-form blog
    2. Format and enhance the blog
    3. Insert CTA into the blog
    4. Write a newsletter from the idea
    5. Create 3–5 social media snippets
    6. Generate reels, images, videos, and blog idea/image prompts

✅ Final result should be a fully structured content pack.
""",
    tools=[
        blog_tool,
        formatter_tool,
        cta_tool,
        newsletter_tool,
        snippets_tool,
        reels_tool,
        social_image_tool,
        blog_ideas_tool,
        blog_image_tool,
        image_tool,
        video_tool
    ],
    model=model
)

# === Automation Runner ===
async def run_content_orchestrator_agent(idea: str) -> str:
    if not idea:
        idea = "AI in business"
    input_data = [{"role": "user", "content": idea}]
    result = await Runner.run(content_orchestrator, input_data)
    return result.final_output

# === Export as Tool ===
def get_content_orchestrator_tool():
    return content_orchestrator.as_tool(
        tool_name="content_orchestrator",
        tool_description="Create a full content pack using blog, CTA, newsletter, social snippets, and visual content"
    )

# === Optional CLI Runner ===
if __name__ == "__main__":
    async def cli():
        print("🧠 Content Creation Orchestrator Ready!")
        while True:
            idea = input("💡 Enter a content idea (or 'exit'): ").strip()
            if idea.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break
            output = await run_content_orchestrator_agent(idea)
            print("\n📦 Final Output:\n", output)

    asyncio.run(cli())
