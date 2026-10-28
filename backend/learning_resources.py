import os
import re
import math
import requests

from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone


# -----------------------------------------
# 1. Configuration
# -----------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)

YOUTUBE_VIDEOS_URL = (
    "https://www.googleapis.com/youtube/v3/videos"
)


# -----------------------------------------
# 2. Convert ISO 8601 duration to seconds
# -----------------------------------------

def duration_to_seconds(duration):
    pattern = (
        r"PT"
        r"(?:(\d+)H)?"
        r"(?:(\d+)M)?"
        r"(?:(\d+)S)?"
    )

    match = re.fullmatch(pattern, duration or "")

    if not match:
        return 0

    hours, minutes, seconds = match.groups()

    return (
        int(hours or 0) * 3600
        + int(minutes or 0) * 60
        + int(seconds or 0)
    )


def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours:
        return f"{hours}h {minutes}m"

    return f"{minutes}m {remaining_seconds}s"


# -----------------------------------------
# 3. Check skill relevance
# -----------------------------------------

def calculate_relevance(skill, title, description):
    skill = skill.strip().lower()
    title = title.lower()
    description = description.lower()

    # Normalize common punctuation.
    title = re.sub(r"[^a-z0-9+#. ]", " ", title)
    description = re.sub(
        r"[^a-z0-9+#. ]", " ", description
    )

    # First check exact skill phrase in the title.
    if skill in title:
        relevance = 3
    else:
        words = [
            word for word in skill.split()
            if len(word) > 1
        ]

        title_matches = sum(
            1 for word in words if word in title
        )

        description_matches = sum(
            1 for word in words if word in description
        )

        if not words:
            return 0

        if title_matches == len(words):
            relevance = 3
        elif title_matches > 0:
            relevance = 2
        elif description_matches == len(words):
            relevance = 1
        else:
            relevance = 0

    # Higher scores mean stronger relevance.
    return relevance


# -----------------------------------------
# 4. Search YouTube and rank popular courses
# -----------------------------------------

def search_youtube(skill, max_results=5):
    if not API_KEY:
        raise ValueError(
            "YOUTUBE_API_KEY missing. Check your .env file."
        )

    skill = skill.strip()

    if not skill:
        return []

    max_results = max(1, min(int(max_results), 10))

    try:
        # Search candidate videos.
        search_params = {
            "part": "snippet",
            "q": f"{skill} full course tutorial",
            "type": "video",
            "order": "relevance",
            "videoDuration": "long",
            "maxResults": 50,
            "key": API_KEY,
        }

        response = requests.get(
            YOUTUBE_SEARCH_URL,
            params=search_params,
            timeout=20,
        )
        response.raise_for_status()

        search_data = response.json()

        # Collect unique video IDs.
        candidates = {}
        for item in search_data.get("items", []):
            video_id = item.get("id", {}).get("videoId")

            if not video_id or video_id in candidates:
                continue

            candidates[video_id] = item.get("snippet", {})

        if not candidates:
            return []

        # Fetch statistics and actual duration in one API call.
        video_params = {
            "part": "snippet,contentDetails,statistics,status",
            "id": ",".join(candidates.keys()),
            "key": API_KEY,
        }

        response = requests.get(
            YOUTUBE_VIDEOS_URL,
            params=video_params,
            timeout=20,
        )
        response.raise_for_status()

        video_data = response.json()

        results = []

        # Terms that can indicate a course.
        course_terms = [
            "full course",
            "complete course",
            "full tutorial",
            "complete tutorial",
            "crash course",
            "beginner to advanced",
            "masterclass",
            "bootcamp",
        ]

        for item in video_data.get("items", []):
            video_id = item.get("id")
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content = item.get("contentDetails", {})
            status = item.get("status", {})

            title = snippet.get("title", "")
            description = snippet.get("description", "")
            channel = snippet.get("channelTitle", "")

            # Ignore videos that are not publicly available.
            if status.get("privacyStatus") != "public":
                continue

            # Skip videos that cannot be embedded.
            if not status.get("embeddable", True):
                continue

            # Calculate skill relevance.
            relevance = calculate_relevance(
                skill, title, description
            )

            # Remove weak matches.
            if relevance < 2:
                continue

            duration_seconds = duration_to_seconds(
                content.get("duration", "")
            )

            # Only long videos: more than 20 minutes.
            if duration_seconds <= 1200:
                continue

            views = int(statistics.get("viewCount", 0))

            title_lower = title.lower()
            description_lower = description.lower()

            is_course = any(
                term in title_lower
                or term in description_lower
                for term in course_terms
            )

            # Popularity score on a logarithmic scale.
            popularity = math.log10(views + 1)

            # Relevance takes priority over popularity.
            # A highly viewed unrelated video must not win.
            ranking_score = (
                relevance * 100
                + popularity * 5
                + (10 if is_course else 0)
            )

            published_at = snippet.get("publishedAt", "")

            results.append({
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "url": (
                    f"https://www.youtube.com/watch?v={video_id}"
                ),
                "thumbnail": (
                    snippet.get("thumbnails", {})
                    .get("high", {})
                    .get("url", "")
                ),
                "views": views,
                "duration_seconds": duration_seconds,
                "duration": format_duration(duration_seconds),
                "published_at": published_at,
                "skill": skill,
                "relevance_score": relevance,
                "is_course": is_course,
                "ranking_score": round(ranking_score, 2),
            })

        # Sort by relevance, then popularity and course indicators.
        results.sort(
            key=lambda video: (
                video["ranking_score"],
                video["views"],
            ),
            reverse=True,
        )

        # Remove internal scoring fields from public output.
        final_results = []

        for video in results[:max_results]:
            video.pop("ranking_score", None)
            final_results.append(video)

        return final_results

    except requests.exceptions.HTTPError as error:
        # Do not print the API URL; it may contain the key.
        status_code = (
            error.response.status_code
            if error.response is not None
            else "unknown"
        )

        raise RuntimeError(
            f"YouTube API HTTP error: {status_code}. "
            "Check API restrictions, quota and API status."
        ) from None

    except requests.exceptions.RequestException:
        raise RuntimeError(
            "Could not connect to YouTube API. "
            "Check your internet connection."
        ) from None


# -----------------------------------------
# 5. Test the function
# -----------------------------------------

if __name__ == "__main__":
    skill = input(
        "Enter a skill to search (e.g. Python, SQL, Power BI): "
    ).strip()

    try:
        videos = search_youtube(skill, max_results=5)

        print(f"\nTop videos for: {skill}")
        print("=" * 65)

        if not videos:
            print(
                "No suitable long videos found. "
                "Try another skill name."
            )

        for rank, video in enumerate(videos, start=1):
            print(f"\n{rank}. {video['title']}")
            print(f"   Channel: {video['channel']}")
            print(f"   Views: {video['views']:,}")
            print(f"   Duration: {video['duration']}")
            print(f"   Course indicator: {video['is_course']}")
            print(f"   URL: {video['url']}")

    except (RuntimeError, ValueError) as error:
        print(f"\nError: {error}")
