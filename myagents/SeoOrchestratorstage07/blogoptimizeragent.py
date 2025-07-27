# ============================================
# ✅ Agent 3: blogoptimizeragent.py
# ============================================

import os
import asyncio
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
class BlogOptimizerInput(BaseModel):
    blog_text: str

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Optimize the following blog content for SEO and readability:\n\n"
                f"{self.blog_text}\n\n"
                "Make it clearer, improve sentence structure, and add a tip at the end if needed."
            )
        }]

# ========== Tool ==========
@function_tool
def optimize_blog_content(blog_text: str) -> str:
    """
    Optimizes blog content for SEO and readability.
    """
    try:
        prompt = BlogOptimizerInput(blog_text=blog_text).to_prompt()
        result = asyncio.run(Runner.run(blogoptimizer_agent, prompt))
        return result.final_output or "⚠️ No optimized content generated."
    except Exception as e:
        return f"❌ Error optimizing blog: {str(e)}"

# ========== Agent ==========
blogoptimizer_agent = Agent(
    name="BlogOptimizerAgent",
    instructions=(
        "You're a blog content optimizer. Improve SEO, readability, and clarity.\n"
        "✅ Make sentences cleaner, remove filler words, and keep it engaging.\n"
        "✅ You may suggest tips or improvements at the end.\n"
        "⚠️ If content is already optimized, just improve flow slightly."
    ),
    tools=[optimize_blog_content],
    model=model
)

# ========== Automation Entry ==========
async def run_blogoptimizer_agent(blog_text: str) -> str:
    try:
        prompt = BlogOptimizerInput(blog_text=blog_text).to_prompt()
        result = await Runner.run(blogoptimizer_agent, prompt)
        return result.final_output or "⚠️ No optimized content generated."
    except Exception as e:
        return f"❌ Automation Error: {str(e)}"

# ========== Tool Export ==========
def get_blogoptimizer_tool():
    return blogoptimizer_agent.as_tool(
        tool_name="blogoptimizer_tool",
        tool_description="Optimizes blog content for SEO, clarity, and better readability."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("✍️ Blog Optimizer Agent Ready!")
        while True:
            blog_text = input("📝 Paste blog content to optimize (or 'exit'): ").strip()
            if blog_text.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            try:
                prompt = BlogOptimizerInput(blog_text=blog_text).to_prompt()
                result = await Runner.run(blogoptimizer_agent, prompt)
                print("\n✅ Optimized Blog Content:\n")
                print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
