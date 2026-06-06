import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Topic, Sentiment, Narrative, Speech

router = APIRouter()


@router.get("/topics")
async def get_topics(
    time_range: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """获取所有主题及出现次数"""
    query = select(Topic.topic_name, func.count(Topic.id).label("count"), func.avg(Topic.relevance_score).label("avg_relevance"))

    if time_range:
        if time_range == "1y":
            query = query.join(Speech).where(Speech.date >= datetime(2025, 1, 1))  # simplified
        elif time_range == "5y":
            query = query.join(Speech).where(Speech.date >= datetime(2021, 1, 1))

    query = query.group_by(Topic.topic_name).order_by(func.count(Topic.id).desc()).limit(limit)
    result = await db.execute(query)
    return [
        {"topic": row[0], "count": row[1], "avg_relevance": round(float(row[2]), 3) if row[2] else 0}
        for row in result
    ]


@router.get("/topics/evolution")
async def get_topic_evolution(
    topic: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """主题随时间的热度演化数据（用于河流图）"""
    query = select(
        func.date_trunc("quarter", Speech.date).label("period"),
        Topic.topic_name,
        func.avg(Topic.relevance_score).label("intensity"),
        func.count(Topic.id).label("mentions"),
    ).join(Topic, Topic.speech_id == Speech.id)

    if topic:
        query = query.where(Topic.topic_name == topic)

    query = query.group_by(text("period"), Topic.topic_name).order_by(text("period"))
    result = await db.execute(query)

    return [
        {
            "period": row[0].isoformat() if row[0] else None,
            "topic": row[1],
            "intensity": round(float(row[2]), 3) if row[2] else 0,
            "mentions": row[3],
        }
        for row in result
    ]


@router.get("/sentiment/trend")
async def get_sentiment_trend(
    db: AsyncSession = Depends(get_db),
):
    """情感趋势（用于折线图）"""
    query = select(
        func.date_trunc("month", Speech.date).label("period"),
        Sentiment.sentiment_label,
        func.count(Sentiment.id).label("count"),
    ).join(Sentiment, Sentiment.speech_id == Speech.id) \
     .group_by(text("period"), Sentiment.sentiment_label) \
     .order_by(text("period"))

    result = await db.execute(query)
    return [
        {
            "period": row[0].isoformat() if row[0] else None,
            "label": row[1],
            "count": row[2],
        }
        for row in result
    ]


@router.get("/narratives")
async def get_narratives(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """叙事框架分析结果"""
    query = select(
        Narrative.narrative_name,
        Narrative.category,
        func.count(Narrative.id).label("occurrences"),
        func.avg(Narrative.significance).label("avg_significance"),
    )

    if category:
        query = query.where(Narrative.category == category)

    query = query.group_by(Narrative.narrative_name, Narrative.category) \
                 .order_by(func.count(Narrative.id).desc())

    result = await db.execute(query)
    return [
        {
            "name": row[0],
            "category": row[1],
            "occurrences": row[2],
            "significance": round(float(row[3]), 3) if row[3] else 0,
        }
        for row in result
    ]


@router.get("/keywords")
async def get_keywords_cloud(
    db: AsyncSession = Depends(get_db),
):
    """所有关键词聚合（用于词云）"""
    query = select(Topic.keywords)
    result = await db.execute(query)
    keywords = []
    for row in result:
        if row[0]:
            keywords.extend(row[0])

    # 统计词频
    from collections import Counter
    freq = Counter(keywords).most_common(100)

    return [{"word": word, "count": count} for word, count in freq]
