"""
Simple Web Search Demo
Demonstrates the web search capability without voice
"""

from tools_web_search import WebSearchTool

print("\n🌐 Web Search Tool Demo\n")
print("=" * 60)

# Create tool
web_tool = WebSearchTool()

# Test queries
test_queries = [
    "Python asyncio tutorial",
    "latest AI news",
    "weather forecast",
    "Bitcoin price",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{i}. Query: \"{query}\"")
    print("-" * 60)
    result = web_tool._run(query, max_results=3)
    print(result)
    print()

print("=" * 60)
print("✅ Web Search Demo Complete!")
print("\nThis tool can be integrated into the voice assistant")
print("to answer current information queries.\n")
