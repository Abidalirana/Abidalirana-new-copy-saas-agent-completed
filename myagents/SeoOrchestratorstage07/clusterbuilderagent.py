# ============================================
# ✅ Agent 2: clusterbuilderagent.py
# ============================================

import os
import asyncio
from agents import Agent, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List, Dict

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
class ClusterBuilderInput(BaseModel):
    keywords: List[str]

    def to_prompt(self):
        return [{
            "role": "user",
            "content": (
                f"Group the following keywords into logical SEO topic clusters:\n\n"
                f"{', '.join(self.keywords)}\n\n"
                "Output should be a dictionary-like structure where each main topic has related keywords."
            )
        }]

# ========== Tool ==========
@function_tool
def build_topic_clusters(keywords: List[str]) -> Dict[str, List[str]]:
    """
    Groups given keywords into logical topic clusters for SEO.
    """
    try:
        prompt = ClusterBuilderInput(keywords=keywords).to_prompt()
        result = asyncio.run(Runner.run(cluster_builder_agent, prompt))
        return result.final_output or {"⚠️ No clusters generated.": keywords}
    except Exception as e:
        return {"❌ Error": [str(e)]}

# ========== Agent ==========
cluster_builder_agent = Agent(
    name="ClusterBuilderAgent",
    instructions=(
        "You are an SEO topic cluster generator. Given a list of keywords, your task is to group them into logical clusters.\n"
        "✅ Focus: Group semantically similar keywords together under one topic.\n"
        "⚠️ Output format should be dictionary-style clusters."
    ),
    tools=[build_topic_clusters],
    model=model
)

# ========== Automation Entry ==========
async def run_cluster_builder_agent(keywords: List[str]) -> Dict[str, List[str]]:
    try:
        prompt = ClusterBuilderInput(keywords=keywords).to_prompt()
        result = await Runner.run(cluster_builder_agent, prompt)
        return result.final_output or {"⚠️ No clusters generated.": keywords}
    except Exception as e:
        return {"❌ Automation Error": [str(e)]}

# ========== Tool Export ==========
def get_cluster_builder_tool():
    return cluster_builder_agent.as_tool(
        tool_name="cluster_builder_tool",
        tool_description="Groups keywords into topic clusters for SEO purposes."
    )

# ========== CLI (Optional Manual Test) ==========
if __name__ == "__main__":
    async def main():
        print("📚 Cluster Builder Agent Ready!")
        while True:
            kws = input("📝 Enter keywords separated by commas (or 'exit'): ").strip()
            if kws.lower() in ["exit", "quit"]:
                print("👋 Exiting.")
                break

            keywords = [k.strip() for k in kws.split(",") if k.strip()]

            try:
                prompt = ClusterBuilderInput(keywords=keywords).to_prompt()
                result = await Runner.run(cluster_builder_agent, prompt)
                print("\n📂 Clusters:\n")
                print(result.final_output)
            except Exception as e:
                print("❌ Error:", str(e))

    asyncio.run(main())
