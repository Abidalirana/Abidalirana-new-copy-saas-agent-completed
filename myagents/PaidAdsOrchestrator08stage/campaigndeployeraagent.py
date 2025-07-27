# campaigndeployeraagent.py

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
class CampaignDeployInput(BaseModel):
    platform: str
    budget: str
    schedule: str

    def to_messages(self):
        return [
            {
                "role": "user",
                "content": (
                    f"Deploy a campaign on '{self.platform}' with a budget of '{self.budget}' "
                    f"scheduled for '{self.schedule}'. Confirm deployment and include key setup details."
                )
            }
        ]

# ========== Tools ==========
@function_tool
def deploy_ad_campaign(platform: str, budget: str, schedule: str) -> str:
    """
    Simulates deployment of an ad campaign to the specified platform with a given budget and schedule.
    """
    try:
        if not platform or not budget or not schedule:
            raise ValueError("Missing required deployment input.")

        return (
            f"🚀 Campaign Deployment Summary\n"
            f"Platform: {platform}\n"
            f"Budget: {budget}\n"
            f"Schedule: {schedule}\n\n"
            f"✅ Campaign successfully queued for deployment on {platform}.\n"
            f"Next Steps:\n"
            f"- Verify creative assets\n"
            f"- Monitor performance dashboards\n"
            f"- Optimize based on initial engagement"
        )
    except Exception as e:
        return (
            f"⚠️ Error deploying campaign: {str(e)}\n"
            "Fallback: Use the native ads manager to manually deploy the campaign."
        )

# ========== Agent ==========
campaign_deployer_agent = Agent(
    name="CampaignDeployerAAgent",
    instructions=(
        "You are a Campaign Deployment Agent. Your job is to simulate deploying a campaign to a specified platform "
        "using the provided budget and schedule.\n\n"
        "📤 Deployment Rules:\n"
        "- Confirm deployment details clearly.\n"
        "- Include metadata like platform, budget, schedule.\n"
        "- Offer brief next steps.\n\n"
        "✅ Output Format:\n"
        "- Deployment Metadata\n"
        "- Confirmation Message\n"
        "- Next Steps or Recommendations"
    ),
    tools=[deploy_ad_campaign],
    model=model
)

# ========== Runner ==========
if __name__ == "__main__":

    async def main():
        print("🚀 Campaign Deployer Agent Ready!")
        while True:
            platform = input("🌐 Enter Platform (e.g., Meta, Google): ").strip()
            budget = input("💸 Enter Budget (e.g., $1000): ").strip()
            schedule = input("🗓️ Enter Schedule (e.g., next 14 days): ").strip()

            if any(x.lower() in ["exit", "quit"] for x in [platform, budget, schedule]):
                print("👋 Exiting. Bye!")
                break

            if not platform or not budget or not schedule:
                print("⚠️ Please provide all inputs.\n")
                continue

            input_data = CampaignDeployInput(
                platform=platform,
                budget=budget,
                schedule=schedule
            ).to_messages()

            try:
                result = await Runner.run(campaign_deployer_agent, input_data)
                print(result.final_output)
            except Exception as e:
                print(f"❌ Deployment failed. Please deploy manually if needed. (Error: {e})")

    asyncio.run(main())

# ========== Automation Entry Point ==========
async def run_campaign_deployer_agent(platform: str, budget: str, schedule: str) -> str:
    """
    Programmatic runner for CampaignDeployerAAgent – used by orchestrator.
    """
    if not platform or not budget or not schedule:
        return "⚠️ Missing required data for deployment."

    input_data = CampaignDeployInput(
        platform=platform,
        budget=budget,
        schedule=schedule
    ).to_messages()

    try:
        result = await Runner.run(campaign_deployer_agent, input_data)
        return result.final_output or "⚠️ No output generated. Try again."
    except Exception as e:
        return (
            f"⚠️ Exception occurred: {e}\n"
            "Fallback: Use platform's dashboard to deploy manually."
        )
#===========================
# ========== Tool Export Function ========== #
def get_campaign_deployer_agent_tool():
    """
    Exposes CampaignDeployerAAgent as a tool for orchestrators.
    """
    return campaign_deployer_agent.as_tool(
        tool_name="campaign_deployer_agent",
        tool_description="Simulates ad campaign deployment with platform, budget, and schedule inputs."
    )

