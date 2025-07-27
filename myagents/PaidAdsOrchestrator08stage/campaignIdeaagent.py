# campaignIdeaagent.py

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
class CampaignIdeaInput(BaseModel):
    icp: str
    industry_trend: str

    def to_messages(self):
        return [
            {"role": "user", "content": f"Based on the Ideal Customer Profile: {self.icp}, and current trend: {self.industry_trend}, generate a unique and creative digital ad campaign idea."}
        ]

# ========== Tools ==========
@function_tool
def suggest_ad_campaign(icp: str, industry_trend: str) -> str:
    """
    Suggest a digital ad campaign idea based on the ICP and current trend.
    """
    try:
        if not icp or not industry_trend:
            raise ValueError("Missing ICP or trend information.")

        return (
            f"📢 Campaign Concept: 'Disrupt the Norm'\n"
            f"🎯 Target Audience: {icp}\n"
            f"🔥 Trend Theme: {industry_trend}\n"
            f"💡 Idea: Launch a viral UGC challenge encouraging your audience to share how they 'disrupt the norm' in their industry. Use TikTok + Instagram Reels + Meta Ads. Incorporate gamified CTA & influencer amplification."
        )
    except Exception as e:
        return (
            f"⚠️ Error generating campaign idea: {str(e)}\n"
            "Fallback idea: 'Create a limited-time offer campaign focusing on solving the top pain point of your ICP, using emotional storytelling + social proof.'"
        )

# ========== Agent ==========
campaign_idea_agent = Agent(
    name="CampaignIdeaAgent",
    instructions=(
        "You are a Campaign Strategy Assistant. Your job is to create a unique digital ad campaign idea based on ICP (Ideal Customer Profile) and a trending topic.\n\n"
        "🧠 Strategy Rules:\n"
        "- Focus on making the idea original, engaging, and trend-aligned.\n"
        "- Always include a campaign name, audience focus, and distribution suggestion.\n"
        "- Mention platforms, hooks, or any interactive angle.\n"
        "- Fall back with a general campaign template if data is missing or malformed.\n\n"
        "✅ Output Format:\n"
        "- Campaign Title\n"
        "- Target ICP\n"
        "- Trend Theme\n"
        "- Campaign Idea (3-5 lines max)\n\n"
        "⚠️ Avoid buzzwords and generic filler. Make it crisp and usable."
    ),
    tools=[suggest_ad_campaign],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("📣 Campaign Idea Agent Ready!")
        while True:
            icp = input("👤 Enter your Ideal Customer Profile (ICP): ").strip()
            trend = input("📈 Enter a relevant industry trend: ").strip()
            if icp.lower() in ["exit", "quit"] or trend.lower() in ["exit", "quit"]:
                print("👋 Exiting. Bye!")
                break

            if not icp or not trend:
                print("⚠️ Please enter both ICP and trend.\n")
                continue

            input_data = [{"role": "user", "content": f"Based on the Ideal Customer Profile: {icp}, and current trend: {trend}, generate a unique and creative digital ad campaign idea."}]
            try:
                result = await Runner.run(campaign_idea_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Agent failed. Fallback idea:\nUse a storytelling angle that highlights your customer's pain and your solution. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_campaign_idea_agent(icp: str, industry_trend: str) -> str:
    """
    Programmatic runner for CampaignIdeaAgent – used by orchestrator.
    """
    if not icp or not industry_trend:
        return "⚠️ Missing required data for campaign generation."

    input_data = [{"role": "user", "content": f"Based on the Ideal Customer Profile: {icp}, and current trend: {industry_trend}, generate a unique and creative digital ad campaign idea."}]
    try:
        result = await Runner.run(campaign_idea_agent, input_data)
        return result.final_output or "⚠️ No output from model. Try different input."
    except Exception as e:
        return (
            f"⚠️ Exception occurred: {e}\n"
            "Fallback idea: Run a limited-time promotion with bold visuals and direct CTA. Use Meta + Google Ads with customer pain-based copy."
        )
#==================
# ========== Tool Export Function ========== #
def get_campaign_idea_agent_tool():
    """
    Exposes CampaignIdeaAgent as a tool for orchestrators.
    """
    return campaign_idea_agent.as_tool(
        tool_name="campaign_idea_agent",
        tool_description="Generates unique digital ad campaign ideas using ICP and trending topics."
    )
