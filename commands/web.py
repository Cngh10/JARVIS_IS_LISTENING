import requests
from typing import Optional, Dict, Any, List
from urllib.parse import quote

class WebSearch:
    """Web search and browsing capabilities"""

    def __init__(self):
        self.search_engines = {
            "google": "https://www.google.com/search?q=",
            "duckduckgo": "https://duckduckgo.com/?q=",
            "bing": "https://www.bing.com/search?q="
        }
        self.default_engine = "google"

    def search(self, query: str, engine: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform web search
        Args:
            query: Search query
            engine: Search engine to use (google, duckduckgo, bing)
        """
        try:
            search_engine = engine or self.default_engine
            base_url = self.search_engines.get(search_engine, self.search_engines["google"])

            encoded_query = quote(query)
            search_url = f"{base_url}{encoded_query}"

            # For now, return the URL to open
            # In production, you could use a search API to get actual results
            return {
                "success": True,
                "message": f"Searching for: {query}",
                "url": search_url,
                "engine": search_engine
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Search failed: {str(e)}"
            }

    def open_url(self, url: str) -> Dict[str, Any]:
        """Open a URL in default browser"""
        import subprocess
        import platform

        try:
            system = platform.system()

            if system == "Darwin":  # macOS
                subprocess.run(["open", url])
            elif system == "Linux":
                subprocess.run(["xdg-open", url])
            elif system == "Windows":
                subprocess.run(["start", url], shell=True)

            return {
                "success": True,
                "message": f"Opening {url}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to open URL: {str(e)}"
            }

    def get_weather(self, location: str) -> Dict[str, Any]:
        """
        Get weather information
        Note: This requires a weather API key (OpenWeatherMap, etc.)
        """
        # Placeholder - would need actual API integration
        return {
            "success": False,
            "message": "Weather API not configured. Please add OpenWeatherMap API key."
        }

    def get_time(self, timezone: Optional[str] = None) -> Dict[str, Any]:
        """Get current time"""
        from datetime import datetime
        import pytz

        try:
            if timezone:
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
            else:
                now = datetime.now()

            return {
                "success": True,
                "message": f"The current time is {now.strftime('%I:%M %p')}",
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "formatted": now.strftime("%A, %B %d, %Y at %I:%M %p")
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get time: {str(e)}"
            }

web_search = WebSearch()
