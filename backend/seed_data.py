#!/usr/bin/env python3
"""黄仁勋研究平台 - 种子数据脚本
手动运行：python3 seed_data.py
功能：
1. 创建数据库表
2. 采集种子数据（YouTube 演讲转录 + 财报电话会 + 公开采访）
3. 运行初始分析
"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("seed_data")


async def seed():
    # 确保表存在
    from database.connection import engine
    from database.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表已创建")

    # 采集 YouTube 演讲
    from collectors.youtube import YouTubeCollector
    yt = YouTubeCollector()
    yt_count = await yt.collect()
    logger.info(f"YouTube 采集完成: {yt_count} 篇")

    # 采集新闻/采访
    from collectors.news import NewsCollector
    news = NewsCollector()
    news_count = await news.collect()
    logger.info(f"新闻/采访采集完成: {news_count} 篇")

    # 运行分析
    from analyzers.claude_agent import ClaudeAnalyzer
    analyzer = ClaudeAnalyzer()
    result = await analyzer.analyze_pending()
    logger.info(f"分析完成: {result}")

    # 创建初始快照
    from api.routes_snapshots import create_snapshot
    from database.connection import async_session
    async with async_session() as session:
        snapshot = await create_snapshot.__wrapped__(session)
    logger.info(f"初始快照已创建")

    logger.info("种子数据全部就绪！")


if __name__ == "__main__":
    asyncio.run(seed())
