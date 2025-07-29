import os
import asyncio
import markdown
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

# ========== Schema ==========

class FormatInput(BaseModel):
    markdown_text: str
    cta_text: str = "📢 Enjoyed this content? Follow for more updates!"

# ========== Tool ==========

@function_tool
def format_markdown_to_html(markdown_text: str, cta_text: str = "📢 Enjoyed this content? Follow for more updates!") -> str:
    """
    Converts markdown content to formatted HTML and adds a call-to-action at the bottom.
    """
    html = markdown.markdown(markdown_text)
    full_html = f"{html}<hr><p><strong>{cta_text}</strong></p>"
    return full_html

# ========== Agent ==========

content_formatter_agent = Agent(
    name="ContentFormatterAgent",
    instructions="""
You're a Content Formatting Assistant.

🎯 Your job is to:
- Convert markdown content into clean, structured HTML.
- Append a call-to-action (CTA) message at the bottom.
- Ensure semantic tags are used correctly.
- Output clean HTML, ready for publishing on websites.

✅ Always use the `format_markdown_to_html` tool for formatting.
""",
    tools=[format_markdown_to_html],
    model=model
)

# ========== CLI Mode ==========

if __name__ == "__main__":
    async def main():
        print("🛠️ Content Formatter Agent Ready!")
        while True:
            md = input("📝 Paste your markdown content (or type 'exit'): ").strip()
            if md.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            input_data = [{"role": "user", "content": f"Format this content to HTML:\n\n{md}"}]
            result = await Runner.run(content_formatter_agent, input_data)
            print("\n🔧 HTML Output:\n")
            print(result.final_output)

    asyncio.run(main())

# ========== Automation Entry Point ==========

async def run_content_formatter_agent(markdown_text: str) -> str:
    """
    Automation runner for ContentFormatterAgent.
    Call this from orchestrator: await run_content_formatter_agent("# My Markdown Title")
    """
    if not markdown_text:
        markdown_text = "# Sample\nThis is default content."

    input_data = [{"role": "user", "content": f"Format this content to HTML:\n\n{markdown_text}"}]
    result = await Runner.run(content_formatter_agent, input_data)
    return result.final_output

# ========== Export as Tool ==========

def get_content_formatter_agent_tool():
    """
    Exported ContentFormatterAgent as a tool for orchestrator or other agents.
    """
    return content_formatter_agent.as_tool(
        tool_name="content_formatter",
        tool_description="Convert markdown to clean HTML with CTA at bottom"
    )
