import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 🛑 ENTERPRISE CONNECTION POOL
# ==========================================
# Create a global pool of reusable connections (Min 1, Max 10)
# 10 is perfectly safe for Neon's free tier and plenty for our traffic
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        os.environ["DATABASE_URL"]
    )
    if db_pool:
        print("✅ PostgreSQL Connection pool created successfully.")
except Exception as e:
    print(f"❌ Error creating connection pool: {e}")

def init_db():
    conn = db_pool.getconn()
    try:
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
    except Exception as e:
        print(f"Database Init Error: {e}")
    finally:
        db_pool.putconn(conn) # Return connection to the pool!

def save_preferences(email, keywords, domain, frequency, summary_type, num_articles, top_n, schedule_time=None, schedule_day=None, monthly_week=None, monthly_day=None):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
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
    except Exception as e:
        print(f"Save Preferences Error: {e}")
    finally:
        db_pool.putconn(conn)

def load_preferences(email):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cur.fetchone()
        cur.close()
        return dict(user_data) if user_data else {}
    except Exception as e:
        print(f"Load Preferences Error: {e}")
        return {}
    finally:
        db_pool.putconn(conn)

def get_all_users():
    conn = db_pool.getconn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        return [dict(user) for user in users]
    except Exception as e:
        print(f"Get All Users Error: {e}")
        return []
    finally:
        db_pool.putconn(conn)

def delete_user_profile(email):
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE email = %s;", (email,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        db_pool.putconn(conn)

# Run this once when the file starts
if db_pool:
    init_db()