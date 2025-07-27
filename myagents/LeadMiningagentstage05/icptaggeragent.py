# ✅ Starting Agent 3: icp_tagger_agent.py

# File: icp_tagger_agent.py
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
class LeadProfile(BaseModel):
    name: str
    position: str
    industry: str
    location: str

    def query(self):
        return [{"role": "user", "content": f"Tag this lead: {self.name}, {self.position} in {self.industry}, based in {self.location}."}]

# ========== Tool ==========
@function_tool
def tag_icp_match(name: str, position: str, industry: str, location: str) -> str:
    """
    Tool to tag lead as ICP (Ideal Customer Profile) match or not.
    """
    warm_industries = ["technology", "software", "finance"]
    warm_positions = ["CTO", "VP", "Head", "Director"]

    is_icp = industry.lower() in warm_industries and any(p in position for p in warm_positions)

    return "🔥 Warm Lead (ICP Match)" if is_icp else "❄️ Cold Lead (Not ICP)"

# ========== Agent ==========
icp_tagger_agent = Agent(
    name="ICPTaggerAgent",
    instructions=(
        "You're an ICP Tagger Agent. Your job is to classify if a lead is a warm ICP match based on job title and industry.\n\n"
        "🧠 Intelligence Rules:\n"
        "- Use `tag_icp_match` tool.\n"
        "- Match warm leads based on industry + senior position.\n"
        "- If position is unknown, assume cold lead.\n\n"
        "✅ Response Format:\n"
        "- Status: '🔥 Warm Lead (ICP Match)' or '❄️ Cold Lead (Not ICP)'\n"
        "- Include a one-line reasoning."
    ),
    tools=[tag_icp_match],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🧠 ICP Tagger Agent Ready!")
        while True:
            name = input("👤 Lead Name (or 'exit'): ").strip()
            if name.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break
            position = input("🎓 Position: ").strip()
            industry = input("🏭 Industry: ").strip()
            location = input("📍 Location: ").strip()

            input_data = [{"role": "user", "content": f"Tag this lead: {name}, {position} in {industry}, based in {location}."}]

            try:
                result = await Runner.run(icp_tagger_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_icp_tagger_agent(name: str, position: str, industry: str, location: str) -> str:
    if not all([name, position, industry, location]):
        return "❌ Incomplete lead data."

    input_data = [{"role": "user", "content": f"Tag this lead: {name}, {position} in {industry}, based in {location}."}]
    try:
        result = await Runner.run(icp_tagger_agent, input_data)
        if not result.final_output:
            return "❌ No result for this lead."
        return result.final_output
    except Exception as e:
        return f"⚠️ Failed to tag ICP: {str(e)}"

# 🧪 Uncomment to simulate
# async def test():
#     res = await run_icp_tagger_agent("John Smith", "VP Engineering", "Technology", "NY")
#     print(res)
# asyncio.run(test())
#==================
# ========== Tool Export ========== #
def get_icp_tagger_tool():
    return icp_tagger_agent.as_tool(
        tool_name="tag_icp_lead",
        tool_description="Classifies a lead as a warm ICP match or cold lead based on job title and industry.",
        
    )

