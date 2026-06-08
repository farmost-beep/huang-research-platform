"""调度器 — 管理定时采集、分析和快照生成"""
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running = False

    async def start(self):
        if self._running:
            return

        # 采集任务 — 启动后立即执行，随后按间隔运行
        self.scheduler.add_job(
            self.run_collection,
            "interval",
            hours=settings.collection_interval_hours,
            id="collect_speeches",
            replace_existing=True,
            next_run_time=datetime.utcnow(),
        )

        # 分析任务
        self.scheduler.add_job(
            self.run_analysis,
            "interval",
            hours=settings.analysis_interval_hours,
            id="analyze_speeches",
            replace_existing=True,
            next_run_time=datetime.utcnow(),
        )

        # 快照生成
        self.scheduler.add_job(
            self.run_snapshot,
            "interval",
            days=settings.snapshot_interval_days,
            id="create_snapshot",
            replace_existing=True,
            next_run_time=datetime.utcnow(),
        )

        self.scheduler.start()
        self._running = True
        logger.info("调度器已启动")

    async def stop(self):
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("调度器已停止")

    async def run_collection(self):
        """执行采集管道的所有任务"""
        logger.info("开始数据采集...")
        from collectors.youtube import YouTubeCollector
        from collectors.news import NewsCollector

        collectors = [
            YouTubeCollector(),
            NewsCollector(),
        ]

        for collector in collectors:
            try:
                count = await collector.collect()
                logger.info(f"{collector.__class__.__name__}: 采集 {count} 条")
            except Exception as e:
                logger.error(f"{collector.__class__.__name__} 失败: {e}")

        logger.info("数据采集完成")

    async def run_analysis(self):
        """执行分析管道"""
        logger.info("开始分析...")
        from analyzers.claude_agent import ClaudeAnalyzer

        analyzer = ClaudeAnalyzer()
        try:
            result = await analyzer.analyze_pending()
            logger.info(f"分析完成: {result}")
        except Exception as e:
            logger.error(f"分析失败: {e}")

    async def run_snapshot(self):
        """生成快照"""
        logger.info("生成快照...")
        from database.connection import async_session
        from database.models import Snapshot, Speech, Topic, Sentiment
        from sqlalchemy import select, func

        async with async_session() as session:
            speech_count = (await session.execute(select(func.count(Speech.id)))).scalar()

            topics_result = await session.execute(
                select(Topic.topic_name, func.count(Topic.id).label("count"))
                .group_by(Topic.topic_name)
                .order_by(func.count(Topic.id).desc())
                .limit(50)
            )
            top_topics = [{"topic": r[0], "count": r[1]} for r in topics_result]

            snapshot = Snapshot(
                name=f"自动快照 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                description="自动生成的定期分析快照",
                speech_count=speech_count,
                analysis_data={"top_topics": top_topics},
            )
            session.add(snapshot)
            await session.commit()
            logger.info(f"快照已生成: {snapshot.name}")
