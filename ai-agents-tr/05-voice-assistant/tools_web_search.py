"""
Web Search Tool for CrewAI
Adapted from LocalVLMAgent's implementation
Simple synchronous web search using DuckDuckGo
"""

import re
import httpx
from urllib.parse import quote_plus
from typing import List, Dict
from crewai.tools import BaseTool


class WebSearchTool(BaseTool):
    """
    Web search tool for current information

    Useful for:
    - Current information (weather, news, prices)
    - Technical advice and solutions
    - Market information
    - General knowledge queries
    """

    name: str = "Web Search"
    description: str = (
        "Search the web for current information. "
        "Useful for weather, news, technical advice, market information, "
        "or any real-time data not in the knowledge base."
    )

    def _run(self, query: str, max_results: int = 3) -> str:
        """
        Search the web and return formatted results

        Args:
            query: Search query string
            max_results: Maximum number of results (default: 3)

        Returns:
            Formatted string with search results
        """
        if not query:
            return "Error: Missing search query"

        try:
            results = self._search_duckduckgo(query, max_results)

            if not results:
                return f"No results found for: {query}"

            # Format results for voice assistant
            formatted = f"I found {len(results)} results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                formatted += f"{i}. {result['title']}\n"
                formatted += f"   {result['snippet'][:150]}...\n\n"

            return formatted

        except Exception as e:
            return f"Search error: {str(e)}"

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """
        Search DuckDuckGo Lite and extract results

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of result dictionaries with title, url, snippet
        """
        try:
            encoded_query = quote_plus(query)
            url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)
                if response.status_code != 200:
                    return []

                html = response.text
                results = []

                # DuckDuckGo Lite format
                pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*class=["\']result-link["\'][^>]*>(.*?)</a>.*?<td[^>]*class=["\']result-snippet["\'][^>]*>(.*?)</td>'
                matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

                for match in matches[:max_results]:
                    url = match[0]
                    title = re.sub(r'<[^>]+>', '', match[1]).strip()
                    snippet = re.sub(r'<[^>]+>', '', match[2]).strip()

                    # Clean HTML entities
                    for old, new in [('&amp;', '&'), ('&quot;', '"'), ('&#x27;', "'")]:
                        title = title.replace(old, new)
                        snippet = snippet.replace(old, new)

                    if title and url:
                        results.append({
                            "title": title[:150],
                            "url": url[:300],
                            "snippet": snippet[:300]
                        })

                return results

        except Exception as e:
            print(f"DuckDuckGo search error: {str(e)}")
            return []


# Convenience function
def create_web_search_tool() -> WebSearchTool:
    """Create and return a WebSearchTool instance"""
    return WebSearchTool()


# Test function
if __name__ == "__main__":
    print("Testing Web Search Tool\n")
    tool = create_web_search_tool()

    print("Searching for: 'Python asyncio tutorial'\n")
    result = tool._run("Python asyncio tutorial", max_results=3)
    print(result)
