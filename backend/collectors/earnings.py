"""财报电话会转录采集器"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class EarningsCollector:
    """采集 NVIDIA 财报电话会中黄仁勋的开场陈述和 Q&A"""

    # NVIDIA 财报电话会列表（季度）
    SEED_EARNINGS = [
        # Fiscal Year 2025
        {"quarter": "Q1 FY2026", "date": "2025-05-28", "url": "https://investor.nvidia.com"},
        {"quarter": "Q4 FY2025", "date": "2025-02-26", "url": "https://investor.nvidia.com"},
        {"quarter": "Q3 FY2025", "date": "2024-11-20", "url": "https://investor.nvidia.com"},
        {"quarter": "Q2 FY2025", "date": "2024-08-28", "url": "https://investor.nvidia.com"},
        {"quarter": "Q1 FY2025", "date": "2024-05-22", "url": "https://investor.nvidia.com"},
        # Fiscal Year 2024
        {"quarter": "Q4 FY2024", "date": "2024-02-21", "url": "https://investor.nvidia.com"},
        {"quarter": "Q3 FY2024", "date": "2023-11-21", "url": "https://investor.nvidia.com"},
        {"quarter": "Q2 FY2024", "date": "2023-08-23", "url": "https://investor.nvidia.com"},
        {"quarter": "Q1 FY2024", "date": "2023-05-24", "url": "https://investor.nvidia.com"},
        # Fiscal Year 2023
        {"quarter": "Q4 FY2023", "date": "2023-02-22", "url": "https://investor.nvidia.com"},
        {"quarter": "Q3 FY2023", "date": "2022-11-16", "url": "https://investor.nvidia.com"},
        {"quarter": "Q2 FY2023", "date": "2022-08-24", "url": "https://investor.nvidia.com"},
        {"quarter": "Q1 FY2023", "date": "2022-05-25", "url": "https://investor.nvidia.com"},
    ]

    async def collect(self) -> int:
        """采集财报电话会文本"""
        collected = 0

        for earning in self.SEED_EARNINGS:
            try:
                # 从 SeekingAlpha / Motley Fool 等获取 transcripts
                text = await self._fetch_transcript(earning["quarter"], earning["date"])
                if not text or len(text) < 200:
                    logger.warning(f"未获取到转录: {earning['quarter']}")
                    continue

                from database.connection import async_session
                from database.models import Speech

                async with async_session() as session:
                    from sqlalchemy import select
                    existing = await session.execute(
                        select(Speech).where(
                            Speech.event_name == f"NVIDIA {earning['quarter']} Earnings Call"
                        )
                    )
                    if existing.scalar_one_or_none():
                        logger.info(f"已存在: {earning['quarter']}")
                        continue

                    speech = Speech(
                        title=f"NVIDIA {earning['quarter']} 财报电话会 - 黄仁勋发言",
                        date=datetime.strptime(earning["date"], "%Y-%m-%d"),
                        source_type="earnings",
                        source_url=earning["url"],
                        event_name=f"NVIDIA {earning['quarter']} Earnings Call",
                        raw_text=text,
                        processed_text=text,
                        word_count=len(text.split()),
                    )
                    session.add(speech)
                    await session.commit()
                    collected += 1
                    logger.info(f"采集成功: {earning['quarter']}")

            except Exception as e:
                logger.warning(f"采集失败 {earning['quarter']}: {e}")

        return collected

    async def _fetch_transcript(self, quarter: str, date_str: str) -> Optional[str]:
        """从网络获取财报电话会转录文本"""
        import httpx
        from bs4 import BeautifulSoup

        # 这里实现了基本的网页抓取
        # 实际使用时可以接入 SeekingAlpha API 或 Fool.com 的 transcript
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        urls_to_try = [
            f"https://www.fool.com/earnings/call-transcripts/nvidia-nvda-q-{date_str}/",
            f"https://seekingalpha.com/symbol/NVDA/transcripts",
        ]

        for url in urls_to_try:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(url, headers=headers, follow_redirects=True)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "lxml")
                        # 移除脚本和样式
                        for tag in soup(["script", "style", "nav", "header", "footer"]):
                            tag.decompose()
                        text = soup.get_text(separator="\n")
                        # 提取与 Jensen Huang 相关的部分
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        relevant = []
                        capture = False
                        for line in lines:
                            if "Jensen" in line or "Huang" in line:
                                capture = True
                            if capture:
                                relevant.append(line)
                            if capture and ("Q&A" in line or "Question" in line):
                                break

                        if relevant:
                            return "\n".join(relevant[:500])  # 限制长度
            except Exception:
                continue

        return None
