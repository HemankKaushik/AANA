import os
import time
from datetime import datetime
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph
from tavily import TavilyClient
from groq import Groq

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class State(TypedDict):
    query: str
    domain: str
    days: int
    num_articles: int
    top_n: int
    summary_type: str
    articles: List[Dict[str, Any]]

def search_node(state: State):
    search_query = f"{state['query']} {state['domain']}" if state['domain'] != "General AI" else state['query']
    articles = []
    
    for attempt in range(3):
        try:
            results = tavily.search(
                search_query,
                topic="news",
                max_results=state["num_articles"],
                days=state["days"],
                search_depth="advanced"
            )
            for r in results["results"]:
                articles.append({
                    "title": r["title"],
                    "url": r["url"],
                    "content": r["content"],
                    "published_date": r.get("published_date", "Unknown date"),
                    "summary": "",
                    "tags": []
                })
            break
        except Exception:
            if attempt < 2:
                time.sleep(5)
            else:
                pass 
                
    return {"articles": articles}

def summarize_node(state: State):
    articles = state["articles"]
    today_str = datetime.now().strftime("%B %d, %Y")
    
    for i, article in enumerate(articles):
        try:
            if state["summary_type"] == "Executive Summary":
                prompt = (f"Today is {today_str}. Summarize this article in 1-2 sentences. "
                          f"Only include info from the past {state['days']} day(s). "
                          f"CRITICAL: Output ONLY the summary text. Do not use any introductory phrases like 'Here is a summary' or explain your date logic. Start immediately with the facts.\n\n"
                          f"Title: {article['title']}\n{article['content']}")
            else:
                prompt = (f"Today is {today_str}. Give a detailed technical summary in 2-3 sentences. "
                          f"Focus on developments from the last {state['days']} day(s). "
                          f"CRITICAL: Output ONLY the summary text. Do not use any introductory phrases like 'Here is a summary' or explain your date logic. Start immediately with the facts.\n\n"
                          f"Title: {article['title']}\n{article['content']}")

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            articles[i]["summary"] = response.choices[0].message.content
        except:
            articles[i]["summary"] = "Summary unavailable."
            
    return {"articles": articles}

def tag_node(state: State):
    articles = state["articles"]
    for i, article in enumerate(articles):
        try:
            prompt = f"""You are a technical taxonomy expert. Give exactly 2 specific, hyper-relevant tags for this article.
Rules:
- NO generic tags allowed (e.g., NEVER use 'AI', 'Artificial Intelligence', 'Technology', 'Innovation', 'Machine Learning').
- Tags must be specific to the domain or sub-field.
- Reply with ONLY 2 comma-separated tags.

GOOD EXAMPLES: 'Quantum Error Correction', 'LLM Parameter Tuning', 'Healthcare Predictive Analytics'
BAD EXAMPLES: 'AI', 'Tech News', 'Future'

Article Summary:
{article['summary']}"""

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1  # Add this: Low temperature stops it from hallucinating generic words
            )
            articles[i]["tags"] = [t.strip() for t in response.choices[0].message.content.split(",")]
        except:
            articles[i]["tags"] = []
    return {"articles": articles}

def rank_node(state: State):
    articles = state["articles"]
    top_n = state["top_n"]
    
    if len(articles) <= top_n:
        return {"articles": articles}
        
    summaries = "\n".join([f"{i+1}. {a['title']}: {a.get('summary', a['content'][:200])}" for i, a in enumerate(articles)])
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"You are a news editor. Pick the {top_n} most significant articles. Reply with ONLY the numbers as comma-separated values (e.g. 1,3,5).\n\nArticles:\n{summaries}"}]
        )
        picks = [int(x.strip()) - 1 for x in response.choices[0].message.content.split(",")]
        ranked_articles = [articles[i] for i in picks if 0 <= i < len(articles)][:top_n]
        return {"articles": ranked_articles}
    except:
        return {"articles": articles[:top_n]}

graph = StateGraph(State)
graph.add_node("search", search_node)
graph.add_node("summarize", summarize_node)
graph.add_node("tag", tag_node)
graph.add_node("rank", rank_node)

graph.set_entry_point("search")
graph.add_edge("search", "summarize")
graph.add_edge("summarize", "tag")
graph.add_edge("tag", "rank")
graph.set_finish_point("rank")
compiled_graph = graph.compile()

def run_news_pipeline(query: str, domain: str, days: int, num_articles: int, top_n: int, summary_type: str) -> List[Dict]:
    initial_state = {
        "query": query, "domain": domain, "days": days,
        "num_articles": num_articles, "top_n": top_n,
        "summary_type": summary_type, "articles": []
    }
    result = compiled_graph.invoke(initial_state)
    return result["articles"]