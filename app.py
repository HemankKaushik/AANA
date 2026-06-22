import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from email_dispatch import send_email_digest
from preferences import save_preferences, load_preferences
from agent import run_news_pipeline

load_dotenv()

# ==========================================
# 🔒 THE LOGIN WALL
# ==========================================
if "user_email" not in st.session_state:
    st.title("🤖 AANA Login")
    st.subheader("Access your personalized AI News Agent")
    
    login_email = st.text_input("Enter your email to load your dashboard", placeholder="you@example.com")
    if st.button("Login / Register"):
        if "@" in login_email and "." in login_email:
            st.session_state.user_email = login_email
            st.rerun() # Refreshes the page to let them in
        else:
            st.error("Please enter a valid email address.")
            
    # st.stop() halts the script here. Nobody can see the rest of the app without logging in!
    st.stop() 


# ==========================================
# 📊 THE DASHBOARD (Only visible after login)
# ==========================================
user_email = st.session_state.user_email

# Pull ONLY this specific user's data from the cloud database
saved_prefs = load_preferences(user_email)

FREQUENCY_DAYS = {
    "Real-time": 1,
    "Daily": 1,
    "Weekly": 7,
    "Monthly": 30
}

# --- Main Header ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title("AANA - Autonomous AI News Agent")
with col2:
    if st.button("Log Out"):
        del st.session_state.user_email
        st.rerun()

st.success(f"Logged in securely as: **{user_email}**")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Configure Your Preferences")

keywords = st.sidebar.text_input(
    "Search Keywords",
    value=saved_prefs.get("keywords", "Latest AI news 2026") if saved_prefs else "Latest AI news 2026"
)

domain_list = ["General AI", "Healthcare AI", "FinTech AI", "Robotics", "Cloud AI", "Telecom AI"]
saved_domain = saved_prefs.get("domain", "General AI") if saved_prefs else "General AI"
domain = st.sidebar.selectbox("Domain", domain_list, index=domain_list.index(saved_domain) if saved_domain in domain_list else 0)

summary_list = ["Executive Summary", "Technical Deep-Dive"]
saved_summary = saved_prefs.get("summary_type", "Executive Summary") if saved_prefs else "Executive Summary"
summary_type = st.sidebar.radio("Summary Type", summary_list, index=summary_list.index(saved_summary) if saved_summary in summary_list else 0)

frequency_list = ["Real-time", "Daily", "Weekly", "Monthly"]
saved_freq = saved_prefs.get("frequency", "Real-time") if saved_prefs else "Real-time"
frequency = st.sidebar.selectbox("Delivery Frequency", frequency_list, index=frequency_list.index(saved_freq) if saved_freq in frequency_list else 0)

saved_top_n = saved_prefs.get("top_n", 3) if saved_prefs else 3
top_n = st.sidebar.slider("Number of Top Articles to Receive", 1, 10, int(saved_top_n))

if frequency in ["Weekly", "Monthly"]:
    num_articles = top_n * 3 
else:
    num_articles = top_n * 2

if frequency in ["Daily", "Weekly", "Monthly"]:
    # Time parsing logic for DB retrieval
    saved_time = saved_prefs.get("schedule_time") if saved_prefs else None
    default_time = datetime.strptime(saved_time, "%H:%M:%S").time() if saved_time and saved_time != "None" else None
    schedule_time = st.sidebar.time_input("Select Time", value=default_time)
else:
    schedule_time = None

if frequency == "Weekly":
    day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    saved_day = saved_prefs.get("schedule_day", "Monday") if saved_prefs else "Monday"
    schedule_day = st.sidebar.selectbox("Select Day", day_list, index=day_list.index(saved_day) if saved_day in day_list else 0)
else:
    schedule_day = None

if frequency == "Monthly":
    week_list = ["1st", "2nd", "3rd", "4th"]
    saved_week = saved_prefs.get("monthly_week", "1st") if saved_prefs else "1st"
    monthly_week = st.sidebar.selectbox("Which Week?", week_list, index=week_list.index(saved_week) if saved_week in week_list else 0)
    
    day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    saved_m_day = saved_prefs.get("monthly_day", "Monday") if saved_prefs else "Monday"
    monthly_day = st.sidebar.selectbox("Which Day?", day_list, index=day_list.index(saved_m_day) if saved_m_day in day_list else 0)
else:
    monthly_week = None
    monthly_day = None

st.sidebar.divider()

# --- Save Button ---
if st.sidebar.button("💾 Save Preferences"):
    if not keywords.strip():
        st.sidebar.error("Keywords cannot be empty.")
    else:
        # Notice we are using user_email automatically here!
        save_preferences(
            user_email, keywords, domain, frequency, summary_type,
            num_articles=num_articles,
            top_n=top_n,
            schedule_time=str(schedule_time) if schedule_time else None,
            schedule_day=schedule_day,
            monthly_week=monthly_week,
            monthly_day=monthly_day
        )
        st.sidebar.success("Preferences securely saved to cloud database!")

# --- Manual Trigger Button ---
run_button = st.sidebar.button("🚀 Get AI News Now")

if run_button:
    if not keywords.strip():
        st.error("Please enter at least one keyword.")
        st.stop()

    days = FREQUENCY_DAYS[frequency]

    with st.spinner("AANA is searching, summarizing, and ranking your news..."):
        articles = run_news_pipeline(
            query=keywords,
            domain=domain,
            days=days,
            num_articles=num_articles,
            top_n=top_n,
            summary_type=summary_type
        )
        
    if not articles:
        st.error("Search failed or no articles found. Please try again.")
        st.stop()

    st.success(f"Found {len(articles)} top articles!")

    period_label = {
        "Real-time": "today",
        "Daily": "the last 24 hours",
        "Weekly": "this week",
        "Monthly": "this month"
    }[frequency]

    st.header(f"📰 Top Articles — {period_label.title()}")
    for i, article in enumerate(articles):
        st.markdown(f"### {i+1}. [{article['title']}]({article['url']})")
        if article.get("published_date") and article["published_date"] != "Unknown date":
            st.caption(f"Published: {article['published_date']}")
        st.write(article["summary"])
        if article["tags"]:
            tag_cols = st.columns(len(article["tags"]))
            for j, tag in enumerate(article["tags"]):
                tag_cols[j].success(tag)
        st.divider()

    st.info(f"Delivery: **{frequency}** | Domain: **{domain}** | Email: **{user_email}**")

    with st.spinner("Sending email digest..."):
        success = send_email_digest(user_email, articles)
    if success:
        st.success("Email digest sent!")
    else:
        st.error("Email sending failed. Check your SendGrid settings.")

    # Auto-save after a successful manual run
    save_preferences(
        user_email, keywords, domain, frequency, summary_type,
        num_articles=num_articles, top_n=top_n,
        schedule_time=str(schedule_time) if schedule_time else None,
        schedule_day=schedule_day, monthly_week=monthly_week, monthly_day=monthly_day
    )