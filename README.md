Here is the complete, unbroken README file. You can use the copy button in the top right of this block to grab it all at once:

```markdown
# AANA - Autonomous AI News Agent

An enterprise-grade, fully autonomous AI SaaS platform that researches, summarizes, and delivers personalized AI industry updates directly to users' inboxes. 

AANA operates on a multi-user cloud architecture, utilizing a LangGraph agentic workflow to search the web, compile technical summaries, and dispatch customized newsletters on user-defined schedules.

## 🚀 Key Features

* **Multi-User SaaS Architecture:** Fully decoupled frontend and backend capable of handling multiple concurrent users with individualized delivery schedules.
* **Autonomous AI Pipeline:** Powered by LangGraph, routing dynamic searches through the Tavily API and generating structured summaries via Groq (Llama 3.3 70B).
* **Multi-Threaded Background Scheduler:** A robust, non-blocking Python scheduler that instantly spawns independent background threads to process multiple users simultaneously without missing precise delivery windows.
* **Enterprise Database Management:** Utilizes Neon Serverless PostgreSQL with a custom `SimpleConnectionPool` to aggressively protect active connection limits and ensure high-speed data retrieval.
* **Automated Lifecycle Management:** Built-in "Ghost Sweeper" automatically clears out inactive accounts after 30 days, alongside secure, one-click unsubscribe URL listeners.
* **Cloud-Native Deployment:** Streamlit Cloud handles the interactive UI, while a Render web service quietly runs the persistent background scheduler.

## 🛠️ Tech Stack

* **Agent Framework:** LangGraph
* **LLMs & Search:** Groq (Llama 3.3 70B), Tavily API
* **Cloud Database:** Neon (Serverless PostgreSQL), `psycopg2-binary`
* **Web UI:** Streamlit Cloud
* **Backend Server:** Render (Python Web Service) & Cron-job.org
* **Task Scheduling:** APScheduler (Multi-threaded)
* **Email Dispatch:** SendGrid API

## ⚙️ Architecture Flow

1. **User Portal:** Users log in via the Streamlit interface to configure target keywords, domains, summary types, and precise delivery times.
2. **State Management:** Preferences are securely saved (upserted) into the Neon PostgreSQL database using optimized connection pooling.
3. **The Watcher:** A background APScheduler running on Render polls the database every 60 seconds. 
4. **Agentic Execution:** When a delivery time matches, the scheduler spawns a thread. The LangGraph agent executes a multi-step web search, analyzes the scraped HTML, and compiles an HTML-formatted digest.
5. **Dispatch:** The final payload is injected into a custom SendGrid template and dispatched to the user.

## 💻 Local Setup & Installation

**1. Clone and Environment Setup**
```bash
git clone [https://github.com/yourusername/aana.git](https://github.com/yourusername/aana.git)
cd aana
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

```

**2. Environment Variables**
Create a `.env` file in the root directory with the following keys:

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=your_verified_email
DATABASE_URL=your_neon_postgresql_url

```

**3. Run the Application**
To run the frontend configuration UI:

```bash
streamlit run app.py

```

To run the background scheduler engine (open a second terminal):

```bash
python scheduler.py

```

## 📈 Milestones Completed

* [x] **M0:** Initial Agent Setup and API Integrations
* [x] **M1:** Core LangGraph Research & Summarization Pipeline
* [x] **M2:** Web UI and User Preference Management
* [x] **M3:** SendGrid HTML Dispatch Integration
* [x] **M4:** Multi-User Database Migration (Neon Serverless PostgreSQL)
* [x] **M5:** Multi-threaded Cloud Deployment (Render + Streamlit Cloud)
* [x] **M6:** Security & Lifecycle Optimizations (Connection Pooling, Ghost Sweeper)

