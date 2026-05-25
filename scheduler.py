import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from tavily import TavilyClient
from groq import Groq
from email_dispatch import send_email_digest
from preferences import load_preferences

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_agent():
    print("\n🚀 AANA Agent Running...\n")
    
    # Load user preferences
    prefs = load_preferences()
    if not prefs:
        print("❌ No preferences found. Please set preferences in the app first.")
        return

    print(f"📋 Running for: {prefs['email']}")
    print(f"🔍 Keywords: {prefs['keywords']}")

    # Step 1: Search
    print("\n🔍 Searching for news...")
    results = tavily.search(prefs["keywords"], max_results=3)
    articles = []
    for r in results["results"]:
        articles.append({
            "title": r["title"],
            "url": r["url"],
            "content": r["content"]
        })
    print(f"Found {len(articles)} articles!")

    # Step 2: Summarize
    print("✍️ Summarizing...")
    articles_text = ""
    for i, article in enumerate(articles):
        articles_text += f"\nArticle {i+1}: {article['title']}\n{article['content']}\n"

    if prefs["summary_type"] == "Executive Summary":
        prompt = f"Give a brief executive summary in 3-4 sentences:\n{articles_text}"
    else:
        prompt = f"Give a detailed technical deep-dive summary:\n{articles_text}"

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    summary = response.choices[0].message.content
    print("Summary done!")

    # Step 3: Tag
    print("🏷️ Tagging...")
    tag_response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"Give 3 relevant tags, comma separated only:\n{summary}"
        }]
    )
    tags = [t.strip() for t in tag_response.choices[0].message.content.split(",")]
    print(f"Tags: {tags}")

    # Step 4: Send Email
    print("📧 Sending email...")
    send_email_digest(prefs["email"], articles, summary, tags)
    print("✅ Done!\n")

# Set up scheduler based on frequency
def start_scheduler(frequency="daily"):
    scheduler = BlockingScheduler()

    if frequency == "Real-time":
        # Runs every hour
        scheduler.add_job(run_agent, "interval", hours=1)
        print("⏰ Scheduler set: Every hour")

    elif frequency == "Daily":
        # Runs every day at 8am
        scheduler.add_job(run_agent, "cron", hour=8, minute=0)
        print("⏰ Scheduler set: Daily at 8:00 AM")

    elif frequency == "Weekly":
        # Runs every Monday at 8am
        scheduler.add_job(run_agent, "cron", day_of_week="mon", hour=8, minute=0)
        print("⏰ Scheduler set: Every Monday at 8:00 AM")

    print("🚀 Scheduler started! Press Ctrl+C to stop.\n")
    
    # Run once immediately so you can test it
    run_agent()
    
    scheduler.start()

if __name__ == "__main__":
    # Load preferences to get frequency
    prefs = load_preferences()
    if prefs:
        start_scheduler(prefs["frequency"])
    else:
        print("❌ No preferences found. Open the Streamlit app first and save preferences.")