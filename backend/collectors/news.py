"""新闻/采访转录采集器"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class NewsCollector:
    """采集黄仁勋的媒体采访和公开演讲报道"""

    async def collect(self) -> int:
        """搜索并采集近期黄仁勋相关的采访/新闻"""
        collected = 0

        # 种子 URL 列表 — 黄仁勋知名采访
        seed_interviews = [
            {
                "title": "Stripe Sessions 2025 - Jensen Huang Interview",
                "date": "2025-04-22",
                "source_type": "interview",
                "source_url": "https://stripe.com/sessions",
                "event": "Stripe Sessions 2025",
            },
            {
                "title": "NVIDIA CEO Jensen Huang on AI Boom - 60 Minutes",
                "date": "2024-12-08",
                "source_type": "interview",
                "source_url": "https://www.cbsnews.com/60-minutes/",
                "event": "60 Minutes",
            },
            {
                "title": "Jensen Huang at World Government Summit 2024",
                "date": "2024-02-12",
                "source_type": "conference",
                "source_url": "https://www.worldgovernmentsummit.org/",
                "event": "World Government Summit 2024",
            },
            {
                "title": "Jensen Huang Keynote at SIGGRAPH 2023",
                "date": "2023-08-08",
                "source_type": "conference",
                "source_url": "https://s2023.siggraph.org/",
                "event": "SIGGRAPH 2023",
            },
            {
                "title": "Jensen Huang and Mark Zuckerberg Fireside Chat - SIGGRAPH 2024",
                "date": "2024-07-29",
                "source_type": "conference",
                "source_url": "https://s2024.siggraph.org/",
                "event": "SIGGRAPH 2024",
            },
            {
                "title": "Jensen Huang at AI Summit 2023",
                "date": "2023-09-20",
                "source_type": "conference",
                "source_url": "https://aisummit.org/",
                "event": "AI Summit 2023",
            },
            {
                "title": "Jensen Huang at Stanford Graduate School of Business Viewpoint",
                "date": "2024-03-14",
                "source_type": "interview",
                "source_url": "https://www.gsb.stanford.edu/",
                "event": "Stanford GSB Viewpoint",
            },
            {
                "title": "Jensen Huang at CadenceLIVE 2024",
                "date": "2024-04-10",
                "source_type": "conference",
                "source_url": "https://www.cadence.com/",
                "event": "CadenceLIVE 2024",
            },
        ]

        from database.connection import async_session
        from database.models import Speech

        for interview in seed_interviews:
            try:
                async with async_session() as session:
                    from sqlalchemy import select
                    existing = await session.execute(
                        select(Speech).where(Speech.event_name == interview["event"])
                    )
                    if existing.scalar_one_or_none():
                        continue

                    text = await self._fetch_page_text(interview["source_url"])
                    if text and len(text) > 200:
                        # 尝试找到黄仁勋引用的内容
                        speech = Speech(
                            title=interview["title"],
                            date=datetime.strptime(interview["date"], "%Y-%m-%d"),
                            source_type=interview["source_type"],
                            source_url=interview["source_url"],
                            event_name=interview["event"],
                            raw_text=text[:50000],  # 限制长度
                            processed_text=text[:50000],
                            word_count=len(text.split()),
                            custom_metadata={"status": "placeholder"},
                        )
                        session.add(speech)
                        await session.commit()
                        collected += 1
                        logger.info(f"采集成功: {interview['title']}")
                    else:
                        # 创建占位记录，后续手动填入转录
                        speech = Speech(
                            title=interview["title"],
                            date=datetime.strptime(interview["date"], "%Y-%m-%d"),
                            source_type=interview["source_type"],
                            source_url=interview["source_url"],
                            event_name=interview["event"],
                            raw_text=f"[转录待采集] {interview['title']}",
                            processed_text=f"[转录待采集] {interview['title']}",
                            word_count=0,
                            custom_metadata={"status": "pending_transcript"},
                        )
                        session.add(speech)
                        await session.commit()
                        collected += 1
                        logger.info(f"创建占位: {interview['title']}")

            except Exception as e:
                logger.warning(f"采集失败 {interview['title']}: {e}")

        return collected

    async def _fetch_page_text(self, url: str) -> Optional[str]:
        """获取网页文本"""
        import httpx
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36"
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers=headers, follow_redirects=True)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    for tag in soup(["script", "style", "nav", "footer"]):
                        tag.decompose()
                    return soup.get_text(separator="\n")[:100000]
        except Exception:
            return None
