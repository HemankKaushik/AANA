import os
import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq

load_dotenv()
from preferences import save_preferences, load_preferences

# Load saved preferences if they exist
saved_prefs = load_preferences()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("🤖 AANA - Autonomous AI News Agent")
st.subheader("Get personalized AI news delivered to you")

st.sidebar.header("⚙️ Configure Your Preferences")

# Keywords
keywords = st.sidebar.text_input("Search Keywords", value="Latest AI news 2026")

# Domain filter
domain = st.sidebar.selectbox("Domain", [
    "General AI",
    "Healthcare AI",
    "FinTech AI",
    "Robotics",
    "Cloud AI",
    "Telecom AI"
])

# Number of articles
num_articles = st.sidebar.slider("Number of Articles", 1, 5, 3)

# Summary type
summary_type = st.sidebar.radio("Summary Type", [
    "Executive Summary",
    "Technical Deep-Dive"
])

# Delivery frequency
frequency = st.sidebar.selectbox("Delivery Frequency", [
    "Real-time",
    "Daily",
    "Weekly"
])

# Email input
email = st.sidebar.text_input("Your Email", placeholder="you@example.com")

st.sidebar.divider()
run_button = st.sidebar.button("🚀 Get AI News Now")

if run_button:
    with st.spinner("Searching for AI news..."):
        results = tavily.search(keywords, max_results=num_articles)
        articles = []
        for r in results["results"]:
            articles.append({
                "title": r["title"],
                "url": r["url"],
                "content": r["content"]
            })

    st.success(f"Found {len(articles)} articles!")

    # Show articles
    st.header("📰 Articles Found")
    for i, article in enumerate(articles):
        st.markdown(f"**{i+1}. [{article['title']}]({article['url']})**")

    # Summarize
    with st.spinner("Generating summary..."):
        articles_text = ""
        for i, article in enumerate(articles):
            articles_text += f"\nArticle {i+1}: {article['title']}\n{article['content']}\n"

        if summary_type == "Executive Summary":
            prompt = f"Give a brief executive summary in 3-4 sentences of these AI news articles:\n{articles_text}"
        else:
            prompt = f"Give a detailed technical deep-dive summary of these AI news articles:\n{articles_text}"

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content

    st.header("📝 Summary")
    st.write(summary)

    # Tags
    with st.spinner("Generating tags..."):
        tag_response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"Give 3 relevant tags for this summary. Reply with only comma separated tags:\n{summary}"
            }]
        )
        tags = tag_response.choices[0].message.content.split(",")
        tags = [tag.strip() for tag in tags]

    st.header("🏷️ Tags")
    cols = st.columns(len(tags))
    for i, tag in enumerate(tags):
        cols[i].success(tag)

    st.divider()
    st.info(f"📧 Delivery set to: **{frequency}** | Domain: **{domain}** | Email: **{email if email else 'Not set'}**")
    # Save preferences
    save_preferences(email, keywords, domain, frequency, summary_type)
    st.sidebar.success("✅ Preferences saved!")