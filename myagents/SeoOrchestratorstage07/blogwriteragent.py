# ============================================
# ✅ Agent 3: blogwriteragent.py
# ============================================

import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List

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
class BlogWritingInput(BaseModel):
    topic: str
    keywords: List[str]

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Write a complete blog post on the topic: '{self.topic}'\n"
                f"Make sure to naturally include the following keywords: {', '.join(self.keywords)}.\n"
                f"The post should include an introduction, main body, and conclusion.\n"
                f"Keep the tone informative and engaging."
            )
        }]

# ========== Tool ==========
@function_tool
def write_blog_post(topic: str, keywords: List[str]) -> str:
    """
    Generates a full blog post based on topic and keywords.
    """
    try:
        prompt = BlogWritingInput(topic=topic, keywords=keywords).to_prompt()
        result = asyncio.run(Runner.run(blog_writer_agent, prompt))
        return result.final_output or "⚠️ No blog content generated."
    except Exception as e:
        return f"❌ Error generating blog: {str(e)}"

# ========== Agent ==========
blog_writer_agent = Agent(
    name="BlogWriterAgent",
    instructions=(
        "You are a blog writing assistant. Given a topic and relevant keywords, write a full blog post.\n"
        "✅ Structure: Intro, Body, Conclusion.\n"
        "✅ Use keywords naturally.\n"
        "⚠️ Avoid keyword stuffing. Focus on clarity and readability."
    ),
    tools=[write_blog_post],
    model=model
)

# ========== Automation Entry ==========
async def run_blog_writer_agent(topic: str, keywords: List[str]) -> str:
    try:
        prompt = BlogWritingInput(topic=topic, keywords=keywords).to_prompt()
        result = await Runner.run(blog_writer_agent, prompt)
        return result.final_output or "⚠️ No blog content generated."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== Tool Export ==========
def get_blog_writer_tool():
    return blog_writer_agent.as_tool(
        tool_name="blog_writer_tool",
        tool_description="Generates a complete blog post based on topic and given keywords."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("✍️ Blog Writer Agent Ready!")
        while True:
            topic = input("📝 Enter blog topic (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            keywords_input = input("🔑 Enter keywords separated by commas: ").strip()
            keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

            try:
                prompt = BlogWritingInput(topic=topic, keywords=keywords).to_prompt()
                result = await Runner.run(blog_writer_agent, prompt)
                print("\n📝 Blog Post:\n")
                print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
