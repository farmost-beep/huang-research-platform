"""YouTube 演讲转录采集器"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class YouTubeCollector:
    """采集黄仁勋在 NVIDIA 官方频道和 GTC 的演讲视频转录"""

    # 已知黄仁勋演讲的 YouTube 视频 ID（种子列表）
    SEED_VIDEOS = [
        # GTC Keynotes
        {"id": "Y2FgD5EN5Ig", "title": "GTC 2024 Keynote", "date": "2024-03-18", "event": "GTC 2024"},
        {"id": "_Ff2CqL02M0", "title": "GTC 2023 Keynote", "date": "2023-03-21", "event": "GTC 2023"},
        {"id": "DiI3n1HZZYM", "title": "GTC 2022 Keynote", "date": "2022-03-22", "event": "GTC 2022"},
        {"id": "eA4-2JwwnN4", "title": "GTC 2021 Keynote", "date": "2021-04-12", "event": "GTC 2021"},
        {"id": "JbasD_9wNrs", "title": "GTC 2020 Keynote", "date": "2020-05-14", "event": "GTC 2020"},
        # CES Keynotes
        {"id": "y2KqFQKL8eA", "title": "CES 2025 Keynote", "date": "2025-01-06", "event": "CES 2025"},
        # Computex Keynotes
        {"id": "8B6p9ty1FLE", "title": "Computex 2024 Keynote", "date": "2024-06-02", "event": "Computex 2024"},
        {"id": "j10I9OyPC2c", "title": "Computex 2023 Keynote", "date": "2023-05-28", "event": "Computex 2023"},
    ]

    async def collect(self) -> int:
        """采集 YouTube 演讲转录"""
        collected = 0
        for video in self.SEED_VIDEOS:
            try:
                # 使用 youtube-transcript-api 获取转录
                from youtube_transcript_api import YouTubeTranscriptApi

                transcript_list = YouTubeTranscriptApi.get_transcript(video["id"], languages=["en"])
                raw_text = " ".join([item["text"] for item in transcript_list])

                if len(raw_text) < 100:
                    logger.warning(f"转录过短，跳过: {video['title']}")
                    continue

                # 入库
                from database.connection import async_session
                from database.models import Speech

                async with async_session() as session:
                    from sqlalchemy import select
                    existing = await session.execute(
                        select(Speech).where(Speech.source_url.contains(video["id"]))
                    )
                    if existing.scalar_one_or_none():
                        logger.info(f"已存在，跳过: {video['title']}")
                        continue

                    speech = Speech(
                        title=video["title"],
                        date=datetime.strptime(video["date"], "%Y-%m-%d"),
                        source_type="keynote",
                        source_url=f"https://youtube.com/watch?v={video['id']}",
                        event_name=video["event"],
                        raw_text=raw_text,
                        processed_text=raw_text,
                        word_count=len(raw_text.split()),
                        custom_metadata={"video_id": video["id"]},
                    )
                    session.add(speech)
                    await session.commit()
                    collected += 1
                    logger.info(f"采集成功: {video['title']} ({len(raw_text)}字)")

            except Exception as e:
                logger.warning(f"采集失败 {video['title']}: {e}")

        return collected
