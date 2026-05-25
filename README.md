# AANA - Autonomous AI News Agent

An intelligent autonomous agent that researches, summarizes, and delivers personalized AI industry updates.

## Features
- Autonomous AI news search using Tavily API
- AI-powered summarization using Groq (Llama 3.3 70B)
- Auto-tagging and categorization
- Web configuration portal built with Streamlit
- Automated email digest via SendGrid
- Scheduled delivery (Real-time / Daily / Weekly)

## Tech Stack
- Agent Framework: LangGraph
- LLM: Groq (Llama 3.3 70B)
- Search API: Tavily
- Web UI: Streamlit
- Scheduling: APScheduler
- Email: SendGrid
- Language: Python 3.11+

## Setup
1. Create virtual environment: python -m venv venv
2. Activate: venv\Scripts\activate
3. Install: pip install -r requirements.txt
4. Add API keys to .env file
5. Run app: streamlit run app.py
6. Run scheduler: python scheduler.py

## Milestones
- M0: Setup and Configuration - DONE
- M1: Core Agent Pipeline - DONE
- M2: Web UI - DONE
- M3: Dispatch Pipeline - DONE
- M4: Polish and Documentation - DONE