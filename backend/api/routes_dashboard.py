from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Speech, Topic, Sentiment, Snapshot

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """Dashboard 概览数据"""
    # 基本统计
    total_speeches = (await db.execute(select(func.count(Speech.id)))).scalar()
    total_words = (await db.execute(select(func.coalesce(func.sum(Speech.word_count), 0)))).scalar()

    # 演讲类型分布
    source_dist = await db.execute(
        select(Speech.source_type, func.count(Speech.id).label("count"))
        .group_by(Speech.source_type)
        .order_by(func.count(Speech.id).desc())
    )

    # 时间范围
    earliest = await db.execute(select(func.min(Speech.date)))
    latest = await db.execute(select(func.max(Speech.date)))
    earliest_date = earliest.scalar()
    latest_date = latest.scalar()

    # 最近更新的演讲
    recent = await db.execute(
        select(Speech).order_by(desc(Speech.date)).limit(5)
    )

    # 最新快照
    latest_snapshot = await db.execute(
        select(Snapshot).order_by(desc(Snapshot.created_at)).limit(1)
    )

    return {
        "total_speeches": total_speeches,
        "total_words": total_words,
        "time_range": {
            "earliest": earliest_date.isoformat() if earliest_date else None,
            "latest": latest_date.isoformat() if latest_date else None,
        },
        "source_distribution": [
            {"source": row[0], "count": row[1]} for row in source_dist
        ],
        "recent_speeches": [
            {
                "id": str(s.id),
                "title": s.title,
                "date": s.date.isoformat(),
                "source_type": s.source_type,
            }
            for s in recent.scalars().all()
        ],
        "latest_snapshot": {
            "id": str(s.id),
            "name": s.name,
            "created_at": s.created_at.isoformat(),
        } if (s := latest_snapshot.scalar_one_or_none()) else None,
    }


@router.get("/yearly")
async def get_yearly_stats(db: AsyncSession = Depends(get_db)):
    """按年份统计演讲数量"""
    query = select(
        func.extract("year", Speech.date).label("year"),
        func.count(Speech.id).label("count"),
    ).group_by(text("year")).order_by(text("year"))

    result = await db.execute(query)
    return [{"year": int(row[0]), "count": row[1]} for row in result]
