import os
import time
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
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

def run_user_task(user, days):
    """This runs in the background so it doesn't block the main clock."""
    email = user["email"]
    try:
        articles = run_news_pipeline(
            query=user["keywords"], domain=user["domain"],
            days=days, num_articles=user.get("num_articles", 6),
            top_n=user.get("top_n", 3), summary_type=user.get("summary_type", "Executive Summary")
        )
        if articles:
            success = send_email_digest(email, articles)
            if success:
                print(f"✅ Successfully sent to {email}")
    except Exception as e:
        print(f"❌ Error processing user {email}: {e}")

def check_and_run_dispatches():
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time_str = now.strftime("%H:%M") 
    
    print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Scanning database for scheduled tasks...")
    users = get_all_users()
    
    if not users:
        return

    for user in users:
        email = user["email"]
        freq = user["frequency"]
        
        # Real-time is handled manually on the dashboard, skip it here
        if freq == "Real-time":
            continue
            
        db_time = user.get("schedule_time")
        user_time_str = db_time[:5] if db_time and db_time != "None" else None
        should_run = False

        if freq == "Daily" and user_time_str == current_time_str:
            should_run = True
        elif freq == "Weekly" and user.get("schedule_day") == current_day and user_time_str == current_time_str:
            should_run = True

        if should_run:
            print(f"🚀 Trigger match found for {email}! Spawning background thread...")
            days = FREQUENCY_DAYS.get(freq, 1)
            # Start a background worker immediately so the loop keeps moving instantly
            worker = threading.Thread(target=run_user_task, args=(user, days), daemon=True)
            worker.start()


#  THE RENDER BYPASS HACK

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"AANA Scheduler is alive and running!")

def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("Booting up dummy web server for Render...")
    threading.Thread(target=start_dummy_server, daemon=True).start()
    
    print("AANA Multi-User Scheduler started! (Multi-threaded)")
    scheduler = BlockingScheduler()
    # Check the database every 60 seconds
    scheduler.add_job(check_and_run_dispatches, 'interval', minutes=1)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")