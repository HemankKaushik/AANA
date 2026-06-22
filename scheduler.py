import time
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from preferences import get_all_users
from agent import run_news_pipeline
from email_dispatch import send_email_digest

load_dotenv()

FREQUENCY_DAYS = {
    "Real-time": 1,
    "Daily": 1,
    "Weekly": 7,
    "Monthly": 30
}

def check_and_run_dispatches():
    """This function runs every 1 minute to check the database."""
    now = datetime.now()
    current_day = now.strftime("%A") # e.g., "Monday"
    
    # Streamlit saves time as "HH:MM:SS" (e.g., "14:30:00"). We slice it to just "HH:MM"
    current_time_str = now.strftime("%H:%M") 
    
    print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scanning database for scheduled tasks...")
    
    users = get_all_users()
    
    if not users:
        print("No users found in the database yet.")
        return

    for user in users:
        email = user["email"]
        freq = user["frequency"]
        
        # Grab their scheduled time from the database and format it to match "HH:MM"
        db_time = user.get("schedule_time")
        user_time_str = db_time[:5] if db_time and db_time != "None" else None

        should_run = False

        # --- LOGIC GATES TO CHECK IF WE SHOULD SEND AN EMAIL RIGHT NOW ---
        if freq == "Real-time":
            # For real-time, you might want a separate trigger. We will skip it in the 1-minute cron for now 
            # to avoid spamming APIs, as users usually trigger Real-Time manually in the UI.
            pass 
            
        elif freq == "Daily":
            if user_time_str == current_time_str:
                should_run = True
                
        elif freq == "Weekly":
            if user.get("schedule_day") == current_day and user_time_str == current_time_str:
                should_run = True
                
        # (Monthly logic would go here, matching exact dates)

        if should_run:
            print(f"🚀 Trigger match found for {email}! Booting up LangGraph agent...")
            
            try:
                # 1. Run the AI Pipeline
                articles = run_news_pipeline(
                    query=user["keywords"],
                    domain=user["domain"],
                    days=FREQUENCY_DAYS.get(freq, 1),
                    num_articles=user.get("num_articles", 6),
                    top_n=user.get("top_n", 3),
                    summary_type=user.get("summary_type", "Executive Summary")
                )
                
                # 2. Send the Email
                if articles:
                    success = send_email_digest(email, articles)
                    if success:
                        print(f"✅ Successfully sent scheduled digest to {email}")
                    else:
                        print(f"❌ Failed to send email to {email}")
                else:
                    print(f"⚠️ No articles found for {email} today.")
                    
            except Exception as e:
                print(f"❌ Error processing user {email}: {e}")

if __name__ == "__main__":
    print(" AANA Multi-User Scheduler started! Press Ctrl+C to exit.")
    
    # Create the scheduler
    scheduler = BlockingScheduler()
    
    # Add the job to run exactly every 1 minute
    scheduler.add_job(check_and_run_dispatches, 'interval', minutes=1)
    
    try:
        # Start the infinite loop
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")