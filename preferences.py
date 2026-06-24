import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


# ENTERPRISE CONNECTION POOL (FAIL-SAFE)
# Initialize it as None first so the script doesn't crash if Neon is asleep!
db_pool = None

try:
    # Use .get() so it doesn't throw a KeyError if Streamlit secrets load slightly late
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, db_url)
        print(" PostgreSQL Connection pool created successfully.")
    else:
        print(" DATABASE_URL not found in environment variables.")
except Exception as e:
    print(f" Error creating connection pool: {e}")


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
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_date DATE DEFAULT CURRENT_DATE;")
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Database Init Error: {e}")
    finally:
        db_pool.putconn(conn) # Return connection to the pool

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

def update_last_active(email):
    """Stamps the current date when a user logs in."""
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET last_active_date = CURRENT_DATE WHERE email = %s", (email,))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error updating last active date: {e}")
    finally:
        db_pool.putconn(conn)

def sweep_inactive_users(days_inactive=30):
    """Deletes users who haven't logged in recently."""
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        # PostgreSQL syntax to delete rows older than X days
        cur.execute("DELETE FROM users WHERE last_active_date < CURRENT_DATE - INTERVAL '%s days'", (days_inactive,))
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        
        if deleted_count > 0:
            print(f"🧹 Ghost Sweeper activated: Deleted {deleted_count} inactive accounts.")
        return deleted_count
    except Exception as e:
        print(f"Error sweeping users: {e}")
        return 0
    finally:
        db_pool.putconn(conn)

# Run this once when the file starts
if db_pool:
    init_db()