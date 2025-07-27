import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import (
    Agent,
    Runner,
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
)

# === Load ENV & Config ===
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

# === IMPORT WRAPPED TOOLS ===
from myagents.content.orchestrator02content import get_content_orchestrator_tool
from myagents.trend.orchestrend01 import get_trend_orchestrator_tool
from myagents.publisher03stage.orchestrator03 import get_publisher_orchestrator_tool
from myagents.feedbackandlearningagentstage04.orchestrato04rstagefeedback import get_feedback_orchestrator_tool
from myagents.LeadMiningagentstage05.orchestrator05 import get_lead_mining_orchestrator_tool
from myagents.EmailMarketing06stage.orchestrator06 import get_email_orchestrator_tool
from myagents.SeoOrchestratorstage07.orchestrator07 import get_seo_orchestrator_tool
from myagents.PaidAdsOrchestrator08stage.orchestrator08 import get_paid_ads_orchestrator_tool
from myagents.AnalyticsReportingOrchestratorstage09.orchestrator09 import get_analytics_orchestrator_tool

# === PROMPT SETUP ===
prompt_text = """
Prompt
Day 1 (Monday):
Upwork Profile Optimization and niche research
Tips on creating a standout profile that attracts clients.
Importance of a professional portfolio and testimonials.

Proposal Writing Strategies
How to write compelling proposals that win jobs.
Common mistakes to avoid in proposals.

Time Management
Managing multiple projects and deadlines effectively.
Tools and techniques for better time management.

Day 2 (Tuesday):
Client Communication
Best practices for communicating with clients on Upwork.
Handling difficult clients and conflict resolution.

Pricing and Negotiation
Setting competitive rates while ensuring profitability.
Negotiation tactics to secure better deals.

Freelance Branding
Building a personal brand that stands out in the freelance marketplace.
Leveraging social media to enhance your freelance career.

Day 3 (Thursday):
Freelance Skill Development
Identifying and learning in-demand skills.
Resources for continuous learning and improvement.

Freelance Project Management
Managing projects efficiently using tools like Notion.
Keeping track of milestones, deliverables, and deadlines.

Freelance Community Building
Networking with other freelancers for support and collaboration.
Joining and contributing to freelance communities and forums.

Detailed SOPs for Focus Framework Days

Daily Structure (3-3-2 Cycle)
Day 1 (Monday):
Upwork Profile Optimization
Proposal Writing Strategies
Time Management

Day 2 (Tuesday):
Client Communication
Pricing and Negotiation
Freelance Branding

Day 3 (Thursday):
Skill Development
Project Management
Freelance Community Building

Step-by-Step Process
1. Research
Platform: Reddit and Upwork Forums
Task: Identify common problems and questions posted by freelancers about the day's themes.
Outcome: Gather at least 5–10 relevant issues to address in your content.

2. SEO Optimization
Task: Write an SEO-optimized newsletter addressing the identified problems.
Components:
- Title: Craft a compelling, keyword-rich title.
- Introduction: Start with a relatable scenario or personal anecdote.
- Main Content: Provide actionable insights, frameworks, and tips.
- Conclusion: Summarize key points and include a call-to-action.

3. Content Repurposing
Task: Repurpose the newsletter into an article, LinkedIn post, and Twitter content.
Steps:
- Article: Publish the newsletter as an article on your website.
- LinkedIn:
  - Post: Create an engaging post summarizing the newsletter.
  - Engagement: CTA to read full article, quiz/contest for free template.
- Twitter:
  - Tweet: Value-packed tweet with a catchy hook and CTA.
  - Thread: Detailed explanation with CTA and contest.
  - Engagement: Encourage replies for giveaway.

AIDA Funnel Strategy

LinkedIn AIDA Funnel
Attention: Engaging post
Interest: LinkedIn newsletter
Desire: Giveaway/contest
Action: DM + Website subscription

Twitter AIDA Funnel
Attention: Tweet
Interest: Thread
Desire: Quiz/contest
Action: DM + Website subscription

Series:
- Marketing crime series
- Marketing funnel breakdown series
- Marketing myths series
- Marketing commentary series
- Consumer psychology series
- AIDA framework series

Notion Template Types:
Workbook, Checklist, Planners, Trackers, Calendars, Dashboards, Forms, Templates for SOPs, Kanban boards, Libraries & repositories, Frameworks, Logs, Roadmaps, Action plans, Workflows, Scorecards, Mind maps, Matrixes, Automation, Reports, Blueprints

Execution Plan:
- Create Content Calendar
- Optimize Profiles
- Implement Simple Funnel

Save this and wait for the next instructions.
"""

# === MAIN RUNNER ===
async def run_main_orchestrator():
    print("\n🚀 Welcome to the Main Orchestrator")
    print("Let's start your personalized onboarding.\n")

    print("📘 Prompt Included:\n")
    print(prompt_text[:1000])
    print("...\n")

    user_input = input("💬 Type 'start' to begin answering questions: ").strip()
    if user_input.lower() != 'start':
        print("👋 Exiting setup.")
        return

    # === Load all tools (including async ones)
    content_tool = get_content_orchestrator_tool()
    trend_tool = get_trend_orchestrator_tool()
    publisher_tool = get_publisher_orchestrator_tool()
    feedback_orchestrator_tool = await get_feedback_orchestrator_tool()
    engagement_tool = get_lead_mining_orchestrator_tool()
    refine_tool = get_email_orchestrator_tool()
    postmortem_tool = get_seo_orchestrator_tool()
    followup_tool = get_paid_ads_orchestrator_tool()
    scheduler_tool = get_analytics_orchestrator_tool()

    # === MAIN ORCHESTRATOR AGENT ===
    main_orchestrator = Agent(
        name="MainOrchestrator",
        instructions="""
You are the main orchestrator agent responsible for gathering structured business insights and routing tasks to sub-agents accordingly.

Step-by-step:
1. Review the full set of onboarding answers provided by the user.
2. Based on user needs, trigger the correct tools:
    - Use content_tool to generate social/email/blog/etc.
    - Use trend_tool to analyze market or niche trends.
    - Use email_tool for outreach sequences and nurture emails.
    - Use client_tool to format polished client-facing reports.
    - Use engagement_tool to suggest engagement boosters.
    - Use refine_tool to improve underperforming assets.
    - Use postmortem_tool to run campaign post-mortems.
    - Use followup_tool for nurturing and follow-up automation.
    - Use scheduler_tool to plan and organize campaigns.
3. Combine outputs into one final response.

Focus on understanding:
- Business type, niche, offers, CRM/tools, goals.
- Preferred output type: content, leads, SEO, reports.
- Suggest a personalized AI workflow.
""",
        tools=[
            content_tool,
            trend_tool,
            publisher_tool,
            feedback_orchestrator_tool,
            engagement_tool,
            refine_tool,
            postmortem_tool,
            followup_tool,
            scheduler_tool,
        ],
        model=model
    )

    # === Structured Questions ===
    questions = [
        "What is your business name and website (if any)?",
        "What type of business do you run? (Freelancer, Agency, SaaS, Info-product, eCommerce, Other)",
        "What industry or niche are you in? (e.g., marketing, prop trading, health, fintech)",
        "Is your business B2B or B2C (or both)?",
        "What is your current monthly revenue range? (0, 1–5k, 5–20k, 20k+)",
        "Do you sell one-time offers, retainers/subscriptions, or both?",
        "What is your main product or service?",
        "What is the price point of your offer(s)?",
        "What is your primary marketing goal right now? (Leads, Sales, Audience, SEO, Brand, etc.)",
        "Do you currently use cold outreach, content, SEO, or paid ads? (Select multiple if needed)",
        "What platforms are you active on? (LinkedIn, Twitter, Threads, Email, WordPress, YouTube, Instagram, Other)",
        "Do you have an existing audience or email list? (Yes/No)",
        "Do you want to use AI to generate content, leads, or analytics—or all of them?",
        "Who is your ideal customer? (job title, company type, etc.)",
        "What problems does your audience face?",
        "What outcome do they want?",
        "Which platforms do your target users hang out on most?",
        "Are they cold, warm, or hot leads mostly?",
        "What CRMs or tools are you using? (Lemlist, Brevo, HubSpot, etc.)",
        "Do you have landing pages or a blog already set up? (Yes/No)",
        "Do you run email sequences, campaigns, or newsletters? (Yes/No)",
        "Do you have a sales team, or are you a solo operator?",
        "Do you want a full AI system or human + AI collaboration?",
        "How much manual input are you comfortable with? (0 = full automation, 10 = full control)",
        "What kind of outputs do you want first? (Lead List, Social Content, Email Campaign, Blog Strategy, SEO Plan, Ad Ideas)",
        "Do you want reports and insights weekly, biweekly, or monthly?",
        "Would you like the AI to suggest a custom workflow now? (Yes/No)",
        "Should the AI auto-activate agents after you approve the plan? (Yes/No)",
        "Add any brand tone or personality traits we should match?",
        "Any competitors or references you want us to learn from?",
        "Any 'don’ts' you want us to avoid?"
    ]

    print("\n🧠 Please answer the following questions to tailor the strategy:\n")
    answers = []
    for q in questions:
        a = input(f"📝 {q}\n> ").strip()
        answers.append(f"{q}\n{a}\n")

    onboarding_summary = prompt_text + "\n\n" + "\n".join(answers)

    print("\n📤 Submitting your answers and prompt to the main orchestrator...\n")

    try:
        input_data = [{"role": "user", "content": onboarding_summary}]
        result = await Runner.run(main_orchestrator, input_data)
    except Exception as e:
        print(f"⚠️ Primary format failed: {e}\n👉 Trying raw string format...")
        result = await Runner.run(main_orchestrator, onboarding_summary)

    print("\n✅ Final Combined Output:\n")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(run_main_orchestrator())
