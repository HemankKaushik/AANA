import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    # Connects to the Neon database using your .env URL
    return psycopg2.connect(os.environ["DATABASE_URL"])

def init_db():
    # Creates the table if it doesn't exist yet
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) PRIMARY KEY,
            keywords TEXT,
            domain VARCHAR(100),
            frequency VARCHAR(50),
            summary_type VARCHAR(100),
            num_articles INTEGER,
            top_n INTEGER,
            schedule_time VARCHAR(50),
            schedule_day VARCHAR(50),
            monthly_week VARCHAR(50),
            monthly_day VARCHAR(50)
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def save_preferences(email, keywords, domain, frequency, summary_type, num_articles, top_n, schedule_time=None, schedule_day=None, monthly_week=None, monthly_day=None):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # "Upsert" logic: Insert a new user, but if the email already exists, just update their settings
    cur.execute('''
        INSERT INTO users (email, keywords, domain, frequency, summary_type, num_articles, top_n, schedule_time, schedule_day, monthly_week, monthly_day)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE SET
            keywords = EXCLUDED.keywords,
            domain = EXCLUDED.domain,
            frequency = EXCLUDED.frequency,
            summary_type = EXCLUDED.summary_type,
            num_articles = EXCLUDED.num_articles,
            top_n = EXCLUDED.top_n,
            schedule_time = EXCLUDED.schedule_time,
            schedule_day = EXCLUDED.schedule_day,
            monthly_week = EXCLUDED.monthly_week,
            monthly_day = EXCLUDED.monthly_day;
    ''', (email, keywords, domain, frequency, summary_type, num_articles, top_n, str(schedule_time) if schedule_time else None, schedule_day, monthly_week, monthly_day))
    
    conn.commit()
    cur.close()
    conn.close()

def load_preferences(email):
    # Pulls preferences for one specific user
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    return dict(user_data) if user_data else {}

def get_all_users():
    # We will need this later for the background scheduler to loop through everyone!
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(user) for user in users]

# Run this once when the file starts to ensure the table exists
init_db()