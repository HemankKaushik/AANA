import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

results = client.search("Latest AI news 2026", max_results=3)
print("Search Results:")
for result in results['results']:
    print(f"- {result['title']}")
    print(f"  URL: {result['url']}\n")