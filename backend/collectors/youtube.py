"""YouTube 演讲采集器 + 自动搜索新视频"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class YouTubeCollector:
    """采集黄仁勋在 YouTube 上的最新演讲视频"""

    SEED_VIDEOS = [
        {"id": "DiGB5uAYKAg", "title": "GTC 2023 Keynote", "date": "2023-03-21", "event": "GTC 2023"},
        {"id": "eAn_oiZwUXA", "title": "GTC 2021 Keynote", "date": "2021-04-12", "event": "GTC 2021"},
        {"id": "Z2XlNfCtxwI", "title": "GTC 2019 Keynote", "date": "2019-03-18", "event": "GTC 2019"},
        {"id": "Y2F8yisiS6E", "title": "GTC 2024 Keynote", "date": "2024-03-18", "event": "GTC 2024"},
        {"id": "k82RwXqZHY8", "title": "CES 2025 Keynote", "date": "2025-01-06", "event": "CES 2025"},
        {"id": "pKXDVsWZmUU", "title": "Computex 2024 Keynote", "date": "2024-06-02", "event": "Computex 2024"},
        {"id": "TLzna9__DnI", "title": "Computex 2025 Keynote", "date": "2025-05-18", "event": "Computex 2025"},
    ]

    SEARCH_QUERIES = [
        "Jensen Huang keynote",
        "NVIDIA CEO speech",
    ]

    async def collect(self) -> int:
        """采集：种子转录 + YouTube API 搜索"""
        collected = 0
        collected += await self._collect_seed()
        collected += await self._search_new_videos()
        return collected

    async def _collect_seed(self) -> int:
        """种子列表转录采集"""
        collected = 0
        from youtube_transcript_api import YouTubeTranscriptApi
        from database.connection import async_session
        from database.models import Speech
        from sqlalchemy import select
        import uuid

        for video in self.SEED_VIDEOS:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video["id"], languages=["en"])
                raw_text = " ".join([item["text"] for item in transcript_list])
                if len(raw_text) < 100:
                    continue

                async with async_session() as session:
                    existing = await session.execute(
                        select(Speech).where(Speech.source_url.contains(video["id"]))
                    )
                    if existing.scalar_one_or_none():
                        logger.info(f"  已存在: {video['title']}")
                        continue

                    speech = Speech(
                        id=str(uuid.uuid4()),
                        title=video["title"],
                        date=datetime.strptime(video["date"], "%Y-%m-%d"),
                        source_type="keynote",
                        source_url=f"https://youtube.com/watch?v={video['id']}",
                        event_name=video["event"],
                        raw_text=raw_text,
                        processed_text=raw_text[:5000],
                        word_count=len(raw_text.split()),
                        custom_metadata={"video_id": video["id"]},
                    )
                    session.add(speech)
                    await session.commit()
                    collected += 1
                    logger.info(f"  ✅ 种子: {video['title']}")
            except Exception as e:
                logger.warning(f"  跳过 {video['title']}: {e}")

        return collected

    async def _search_new_videos(self) -> int:
        """YouTube Data API 搜索最新视频"""
        from config import settings
        api_key = settings.youtube_api_key
        if not api_key:
            logger.info("  未配置 YOUTUBE_API_KEY，跳过搜索")
            return 0

        collected = 0
        import httpx
        from database.connection import async_session
        from database.models import Speech
        from sqlalchemy import select
        import uuid

        for query in self.SEARCH_QUERIES:
            try:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "order": "date",
                    "maxResults": 5,
                    "publishedAfter": "2023-01-01T00:00:00Z",
                    "key": api_key,
                }
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    for item in data.get("items", []):
                        vid = item["id"]["videoId"]
                        title = item["snippet"]["title"]
                        published = item["snippet"]["publishedAt"][:10]

                        try:
                            from youtube_transcript_api import YouTubeTranscriptApi
                            tl = YouTubeTranscriptApi.get_transcript(vid, languages=["en"])
                            raw_text = " ".join([t["text"] for t in tl])
                            if len(raw_text) < 100:
                                continue
                        except Exception:
                            continue

                        async with async_session() as session:
                            exists = await session.execute(
                                select(Speech).where(Speech.source_url.contains(vid))
                            )
                            if exists.scalar_one_or_none():
                                continue

                            speech = Speech(
                                id=str(uuid.uuid4()),
                                title=title[:200],
                                date=datetime.strptime(published, "%Y-%m-%d"),
                                source_type="keynote" if "keynote" in title.lower() else "speech",
                                source_url=f"https://youtube.com/watch?v={vid}",
                                raw_text=raw_text,
                                processed_text=raw_text[:5000],
                                word_count=len(raw_text.split()),
                            )
                            session.add(speech)
                            await session.commit()
                            collected += 1
                            logger.info(f"  ✅ 新视频: {title[:50]}")
            except Exception as e:
                logger.warning(f"  搜索失败 ({query}): {e}")

        return collected
