# ========== messagesuggesteragent.py ==========

import os
from agents import Agent, function_tool, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

# ========== Environment Config ==========

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

class MessageSuggestInput(BaseModel):
    lead_context: str

    def to_messages(self):
        return [{
            "role": "user",
            "content": f"Draft a custom outreach message based on: {self.lead_context}"
        }]

# ========== Tool ==========

@function_tool
def suggest_message(lead_context: str) -> str:
    """
    Suggests a personalized message based on lead context.
    """
    if not lead_context:
        return "⚠️ No context provided. Please refine the input."

    return f"👋 Hey there! Noticed your interest in {lead_context}. Thought you'd find this helpful..."

# ========== Agent ==========

message_suggester_agent = Agent(
    name="MessageSuggesterAgent",
    instructions=(
        "You're a lead message assistant. Generate a personalized cold outreach message for a lead based on their engagement and context.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Always use `suggest_message` to generate initial drafts.\n"
        "- Use fallback logic if input is empty.\n"
        "- Keep the tone friendly and helpful.\n"
        "- Highlight shared topics or relevance.\n"
        "💬 Example:\n"
        "- 'Saw you liked a post about B2B SaaS scaling tips. Here's something you might enjoy...'"
    ),
    tools=[suggest_message],
    model=model
)

# ========== Runner Function ==========

async def run(lead_context: str) -> str:
    if not lead_context:
        lead_context = "startup tools"

    messages = [{
        "role": "user",
        "content": f"Draft a custom outreach message based on: {lead_context}"
    }]

    try:
        result = await Runner.run(message_suggester_agent, messages)
        return result.final_output or "⚠️ No message generated."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ========== Tool Export ==========

def get_message_suggester_tool():
    return message_suggester_agent.as_tool(
        tool_name="message_suggester",
        tool_description="Suggests a personalized outreach message based on lead context.",
       
    )
