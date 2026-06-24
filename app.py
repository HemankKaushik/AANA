import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from email_dispatch import send_email_digest
from preferences import save_preferences, load_preferences, delete_user_profile
from agent import run_news_pipeline

load_dotenv()

# --- THE LOGIN WALL ---
if "user_email" not in st.session_state:
    st.title("AANA Login")
    st.subheader("Access your personalized AI News Agent")
    
    login_email = st.text_input("Enter your email to load your dashboard", placeholder="you@example.com")
    if st.button("Login / Register"):
        if "@" in login_email and "." in login_email:
            st.session_state.user_email = login_email
            st.rerun() 
        else:
            st.error("Please enter a valid email address.")
    st.stop() 

# --- THE DASHBOARD ---
user_email = st.session_state.user_email

# Pull this specific user's data from the cloud database
saved_prefs = load_preferences(user_email) or {}

FREQUENCY_DAYS = {
    "Real-time": 1,
    "Daily": 1,
    "Weekly": 7,
    "Monthly": 30
}

# --- Main Header & Warning ---
st.title("AANA Management Console")
st.markdown("Configure your automated target keywords and delivery schedule below.")
st.info("**Notice:** If your scheduled digest does not arrive in your primary inbox, please check your spam folder and add the sender address to your verified contacts.")

# --- Clean Multi-Column Layout (Moved from Sidebar) ---
st.markdown("### Subscription Parameters")

col1, col2 = st.columns(2)

with col1:
    keywords = st.text_input("Target Search Keywords", value=saved_prefs.get("keywords", "Latest AI news 2026"))
    
    domain_list = ["General AI", "Healthcare AI", "FinTech AI", "Robotics", "Cloud AI", "Telecom AI"]
    saved_domain = saved_prefs.get("domain", "General AI")
    domain = st.selectbox("Industry Domain Filter", domain_list, index=domain_list.index(saved_domain) if saved_domain in domain_list else 0)

    summary_list = ["Executive Summary", "Technical Deep-Dive"]
    saved_summary = saved_prefs.get("summary_type", "Executive Summary")
    summary_type = st.radio("Summary Type", summary_list, index=summary_list.index(saved_summary) if saved_summary in summary_list else 0)

    saved_top_n = saved_prefs.get("top_n", 3)
    top_n = st.slider("Number of Top Articles to Receive", 1, 10, int(saved_top_n))

with col2:
    frequency_list = ["Real-time", "Daily", "Weekly", "Monthly"]
    saved_freq = saved_prefs.get("frequency", "Daily")
    frequency = st.selectbox("Delivery Frequency", frequency_list, index=frequency_list.index(saved_freq) if saved_freq in frequency_list else 1)

    # Robust Time Parsing
    saved_time = saved_prefs.get("schedule_time")
    default_time = datetime.strptime("08:00", "%H:%M").time() # Fallback
    if saved_time and saved_time != "None":
        try:
            time_str = str(saved_time)[:5] 
            default_time = datetime.strptime(time_str, "%H:%M").time()
        except Exception:
            pass

    if frequency in ["Daily", "Weekly", "Monthly"]:
        schedule_time = st.time_input("Preferred Delivery Time (IST)", value=default_time)
    else:
        schedule_time = None

    if frequency == "Weekly":
        day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        saved_day = saved_prefs.get("schedule_day", "Monday")
        schedule_day = st.selectbox("Select Day", day_list, index=day_list.index(saved_day) if saved_day in day_list else 0)
    else:
        schedule_day = None

    if frequency == "Monthly":
        week_list = ["1st", "2nd", "3rd", "4th"]
        saved_week = saved_prefs.get("monthly_week", "1st")
        monthly_week = st.selectbox("Which Week?", week_list, index=week_list.index(saved_week) if saved_week in week_list else 0)
        
        day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        saved_m_day = saved_prefs.get("monthly_day", "Monday")
        monthly_day = st.selectbox("Which Day?", day_list, index=day_list.index(saved_m_day) if saved_m_day in day_list else 0)
    else:
        monthly_week = None
        monthly_day = None

if frequency in ["Weekly", "Monthly"]:
    num_articles = top_n * 3 
else:
    num_articles = top_n * 2

st.markdown("---")

# --- Action Buttons ---
button_col1, button_col2 = st.columns(2)

with button_col1:
    if st.button("💾 Save System Preferences", use_container_width=True, type="primary"):
        if not keywords.strip():
            st.error("Keywords cannot be empty.")
        else:
            save_preferences(
                user_email, keywords, domain, frequency, summary_type,
                num_articles=num_articles, top_n=top_n,
                schedule_time=str(schedule_time) if schedule_time else None,
                schedule_day=schedule_day, monthly_week=monthly_week, monthly_day=monthly_day
            )
            st.success("Preferences securely saved to cloud database!")
            st.rerun() # Refresh to show updated values

with button_col2:
    run_button = st.button("🚀 Get AI News Now", use_container_width=True)

# --- Sidebar Account Management ---
with st.sidebar:
    st.markdown(f"**Logged in as:**\n{user_email}")
    if st.button("Log Out", use_container_width=True):
        del st.session_state.user_email
        st.rerun()
        
    st.divider()
    st.markdown("### Account Options")
    if st.checkbox("DELETE MY ACCOUNT"):
        st.warning("Deleting your account will permanently wipe your preferences from our cloud database.")
        if st.button("Permanently Delete My Profile", type="primary"):
            delete_user_profile(user_email)
            del st.session_state.user_email
            st.rerun()

# --- Manual Trigger Logic ---
if run_button:
    if not keywords.strip():
        st.error("Please enter at least one keyword.")
        st.stop()

    days = FREQUENCY_DAYS.get(frequency, 1)

    with st.spinner("AANA is searching, summarizing, and ranking your news..."):
        articles = run_news_pipeline(
            query=keywords, domain=domain, days=days, num_articles=num_articles,
            top_n=top_n, summary_type=summary_type
        )
        
    if not articles:
        st.error("Search failed or no articles found. Please try again.")
        st.stop()

    st.success(f"Found {len(articles)} top articles!")

    period_label = {"Real-time": "today", "Daily": "the last 24 hours", "Weekly": "this week", "Monthly": "this month"}.get(frequency, "today")

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
        # Auto-save after a successful manual run
        save_preferences(
            user_email, keywords, domain, frequency, summary_type,
            num_articles=num_articles, top_n=top_n,
            schedule_time=str(schedule_time) if schedule_time else None,
            schedule_day=schedule_day, monthly_week=monthly_week, monthly_day=monthly_day
        )
    else:
        st.error("Email sending failed. Check your SendGrid settings.")