import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph
from tavily import TavilyClient
from groq import Groq

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define the state
class State(TypedDict):
    query: str
    search_results: list
    summary: str
    tags: list

# Node 1: Search for AI news
def search_node(state: State):
    print("🔍 Searching for AI news...")
    results = tavily.search(state["query"], max_results=3)
    articles = []
    for r in results["results"]:
        articles.append({
            "title": r["title"],
            "url": r["url"],
            "content": r["content"]
        })
    print(f"Found {len(articles)} articles!")
    return {"search_results": articles}

# Node 2: Summarize the results
def summarize_node(state: State):
    print("✍️ Summarizing articles...")
    articles_text = ""
    for i, article in enumerate(state["search_results"]):
        articles_text += f"\nArticle {i+1}: {article['title']}\n{article['content']}\n"

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"Summarize these AI news articles in 3-4 sentences:\n{articles_text}"
        }]
    )
    summary = response.choices[0].message.content
    print("Summary done!")
    return {"summary": summary}

# Node 3: Tag the content
def tag_node(state: State):
    print("🏷️ Tagging content...")
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"Give 3 relevant tags for this AI news summary. Reply with only comma separated tags:\n{state['summary']}"
        }]
    )
    tags = response.choices[0].message.content.split(",")
    tags = [tag.strip() for tag in tags]
    print(f"Tags: {tags}")
    return {"tags": tags}

# Build the graph
graph = StateGraph(State)
graph.add_node("search", search_node)
graph.add_node("summarize", summarize_node)
graph.add_node("tag", tag_node)

graph.set_entry_point("search")
graph.add_edge("search", "summarize")
graph.add_edge("summarize", "tag")
graph.set_finish_point("tag")

app = graph.compile()

# Run it
print("\n🚀 AANA Agent Starting...\n")
result = app.invoke({"query": "Latest AI news 2026"})

print("\n📰 FINAL OUTPUT:")
print("\nArticles Found:")
for article in result["search_results"]:
    print(f"  - {article['title']}")
    print(f"    {article['url']}")

print(f"\nSummary:\n{result['summary']}")
print(f"\nTags: {result['tags']}")