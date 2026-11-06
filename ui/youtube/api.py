"""YouTube Data API v3 client for native YouTube browsing.

Makes standard HTTP requests to the YouTube Data API v3 using only the
standard library's urllib (matching core/media_detect.py's no-new-deps
approach), so no pip install is required beyond what middleTV already has.

All methods run on a background QThread by the screens that use them, never
blocking the UI thread.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

_BASE = "https://www.googleapis.com/youtube/v3"


@dataclass
class Video:
    id: str
    title: str
    channel_title: str
    thumbnail_url: str
    description: str = ""
    duration: str = ""
    view_count: int = 0
    published_at: str = ""


@dataclass
class SearchResult:
    videos: list[Video] = field(default_factory=list)
    next_page_token: Optional[str] = None
    total_results: int = 0


class YouTubeApi:
    """Thin wrapper around YouTube Data API v3.

    Requires an API key (set in Settings -> YouTube API Key, or in
    config/middletv.json as `youtube_api_key`). Without a key the app still
    opens but search/browse calls return empty results with a toast warning.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, path: str, params: dict) -> dict | None:
        if not self.api_key:
            return None
        params = dict(params)
        params["key"] = self.api_key
        url = f"{_BASE}/{path}?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                body = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def search(self, query: str, max_results: int = 25,
               page_token: str | None = None) -> SearchResult:
        """Search YouTube for videos matching query."""
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": str(max_results),
        }
        if page_token:
            params["pageToken"] = page_token
        data = self._get("search", params)
        if not data:
            return SearchResult()
        videos: list[Video] = []
        for item in data.get("items", []):
            snip = item.get("snippet", {})
            videos.append(Video(
                id=item["id"]["videoId"],
                title=snip.get("title", ""),
                channel_title=snip.get("channelTitle", ""),
                thumbnail_url=snip.get("thumbnails", {}).get("medium", {}).get("url", ""),
                description=snip.get("description", ""),
                published_at=snip.get("publishedAt", ""),
            ))
        return SearchResult(
            videos=videos,
            next_page_token=data.get("nextPageToken"),
            total_results=data.get("pageInfo", {}).get("totalResults", 0),
        )

    def video_details(self, video_id: str) -> Video | None:
        """Fetch full details (including duration, view count) for one video."""
        data = self._get("videos", {
            "part": "snippet,contentDetails,statistics",
            "id": video_id,
        })
        if not data or not data.get("items"):
            return None
        item = data["items"][0]
        snip = item.get("snippet", {})
        content = item.get("contentDetails", {})
        stats = item.get("statistics", {})
        return Video(
            id=video_id,
            title=snip.get("title", ""),
            channel_title=snip.get("channelTitle", ""),
            thumbnail_url=snip.get("thumbnails", {}).get("medium", {}).get("url", ""),
            description=snip.get("description", ""),
            duration=content.get("duration", ""),
            view_count=int(stats.get("viewCount", 0)) if stats.get("viewCount") else 0,
            published_at=snip.get("publishedAt", ""),
        )

    def trending(self, max_results: int = 25) -> SearchResult:
        """Most popular videos (trending)."""
        params = {
            "part": "snippet",
            "chart": "mostPopular",
            "regionCode": "US",
            "maxResults": str(max_results),
        }
        data = self._get("videos", params)
        if not data:
            return SearchResult()
        videos: list[Video] = []
        for item in data.get("items", []):
            snip = item.get("snippet", {})
            content = item.get("contentDetails", {})
            stats = item.get("statistics", {})
            videos.append(Video(
                id=item["id"],
                title=snip.get("title", ""),
                channel_title=snip.get("channelTitle", ""),
                thumbnail_url=snip.get("thumbnails", {}).get("medium", {}).get("url", ""),
                description=snip.get("description", ""),
                duration=content.get("duration", ""),
                view_count=int(stats.get("viewCount", 0)) if stats.get("viewCount") else 0,
                published_at=snip.get("publishedAt", ""),
            ))
        return SearchResult(
            videos=videos,
            next_page_token=data.get("nextPageToken"),
            total_results=data.get("pageInfo", {}).get("totalResults", 0),
        )
