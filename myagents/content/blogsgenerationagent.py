# blogsgenerationagent.py

import os
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import AsyncOpenAI
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel

# ========== Configuration ==================================
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

class BlogTopicRequest(BaseModel):
    topic: str

# ========== Tool ==========

@function_tool
def generate_blog_ideas(topic: str) -> str:
    """
    Generate 5 engaging blog ideas based on the input topic.
    """
    return f"Create 5 unique and SEO-friendly blog topics based on: {topic}"

# ========== Agent ==========

blog_post_generator_agent = Agent(
    name="BlogsGenerationAgent",
    instructions="""
You're a Blog Idea Generator.

🎯 Your job is to:
- Generate fresh, valuable blog topics.
- Use the input topic as a seed idea.
- Always run the `generate_blog_ideas` tool to generate titles.

Audience:
- Content marketers
- Bloggers
- SEO specialists
""",
    tools=[generate_blog_ideas],
    model=model
)

# ========== CLI Mode ==========

if __name__ == "__main__":
    async def main():
        print("🧠 Blog Generation Agent Ready!")
        while True:
            user_input = input("💡 Enter a topic for blog ideas (or 'exit'): ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting. See you next time!")
                break

            input_data = [{"role": "user", "content": f"Generate blog topics on: {user_input}"}]
            result = await Runner.run(blog_post_generator_agent, input_data)
            print("\n📝 Suggested Blog Topics:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========

async def run_blog_post_generator_agent(topic: str) -> str:
    """
    Run this function to generate blog ideas from another script or orchestrator.
    """
    if not topic:
        topic = "AI in digital marketing"

    input_data = [{"role": "user", "content": f"Generate blog topics on: {topic}"}]
    result = await Runner.run(blog_post_generator_agent, input_data)
    return result.final_output

# ========== Export as Tool ==========

def get_blog_post_generator_tool():
    """
    Exportable tool for use in orchestrators or other agents.
    """
    return blog_post_generator_agent.as_tool(
        tool_name="blog_post_generator_tool",
        tool_description="Generate 5 creative blog post ideas based on any topic"
    )
