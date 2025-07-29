import os
import sys

# Register root path for agent import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

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

# ========== Schema ========== #
class BlogInput(BaseModel):
    topic: str

# ========== Tool ========== #
@function_tool
def generate_blog_post(topic: str) -> str:
    """
    Expands a short blog topic into a full SEO-optimized blog post.
    """
    return (
        f"# {topic.title()}\n\n"
        f"**Introduction**\n"
        f"Start with a compelling introduction to the topic '{topic}'. Set the tone and explain why the reader should care.\n\n"
        f"**What is {topic}?**\n"
        f"Define the topic clearly and concisely. Provide context or background if needed.\n\n"
        f"**Key Insights**\n"
        f"Explore important details, trends, or research related to '{topic}'. Present factual, relevant information.\n\n"
        f"**Real-World Examples**\n"
        f"- Example 1: Real application of {topic} in industry or society.\n"
        f"- Example 2: Another situation where {topic} has made an impact.\n\n"
        f"**SEO Details**\n"
        f"- **Target Keyword:** `{topic.lower().replace(' ', '-')}`\n"
        f"- **Meta Description:** Discover what {topic} means, its importance, and how it's shaping the future in this full SEO blog post.\n\n"
        f"**Conclusion**\n"
        f"Wrap up with a summary and call to action. Encourage readers to explore more or leave a comment.\n"
    )


# ========== Agent ========== #
# ========== Agent ========== #
blog_writer_agent = Agent(
    name="BlogWriterAgent",
    instructions="""
You're a Blog Writing Assistant.

Your job is to write a full-length blog post based on the topic provided by the user.

🧠 Writing Format & SOP:
Use the following structure strictly:

1. 🎯 Use the AIDA Model:
   - **Attention**: Strong hook headline
   - **Interest**: Describe the problem/need
   - **Desire**: Show benefits or transformation
   - **Action**: Encourage what to do next (e.g., subscribe, share, contact)

2. ✍️ Writing Rules:
   - Use `generate_blog_post` tool.
   - Format using markdown: `#`, `##`, `###` headings.
   - Include: Introduction → Definition → Main Points (3) → Examples (3) → Conclusion (2).
   - Use SEO keywords naturally (e.g., [your_keyword]).
   - Write in a clear, engaging, and professional tone.
   - Add call-to-action at the end.

3. 🔍 Audience:
   - Write for startup founders, marketers, and freelancers.
   - Keep it friendly but expert-level.

✅ Final Output must be ready-to-publish quality for platforms like Notion, Medium, or LinkedIn.
""",


    tools=[generate_blog_post],
    model=model
)

# ========== CLI Mode ========== #
if __name__ == "__main__":

    async def main():
        print("📝 Blog Writer Agent Ready!")
        while True:
            topic = input("🧠 Enter a blog topic (or 'exit'): ").strip()
            if topic.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            if not topic:
                topic = "technology"

            input_data = [{"role": "user", "content": f"Write a blog post on: {topic}"}]
            result = await Runner.run(blog_writer_agent, input_data)
            print("\n📢 Blog Output:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ========== #
async def run_blog_writer_agent(topic: str) -> str:
    """
    Automation runner for BlogWriterAgent.
    Use this in orchestrator: await run_blog_writer_agent("AI in healthcare")
    """
    if not topic:
        topic = "technology"

    input_data = [{"role": "user", "content": f"Write a blog post on: {topic}"}]
    result = await Runner.run(blog_writer_agent, input_data)
    return result.final_output

# ========== Export as Tool ========== #
def get_blog_writer_agent_tool():
    """
    Exported blog writer agent as a tool for orchestrator or other agents.
    """
    return blog_writer_agent.as_tool(
        tool_name="blog_writer",
        tool_description="Generate a full SEO blog post for a given topic"
    )
