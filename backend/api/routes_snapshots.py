from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Snapshot, Speech, Topic, Sentiment

router = APIRouter()


@router.get("/")
async def list_snapshots(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Snapshot).order_by(desc(Snapshot.created_at)).limit(limit)
    )
    snapshots = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "description": s.description,
            "speech_count": s.speech_count,
            "summary": s.summary,
            "created_at": s.created_at.isoformat(),
        }
        for s in snapshots
    ]


@router.get("/latest")
async def get_latest_snapshot(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Snapshot).order_by(desc(Snapshot.created_at)).limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        return {"snapshot": None, "message": "No snapshots yet"}

    return {
        "id": str(snapshot.id),
        "name": snapshot.name,
        "description": snapshot.description,
        "speech_count": snapshot.speech_count,
        "analysis_data": snapshot.analysis_data,
        "summary": snapshot.summary,
        "created_at": snapshot.created_at.isoformat(),
    }


@router.get("/{snapshot_id}")
async def get_snapshot(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Snapshot).where(Snapshot.id == snapshot_id))
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        return {"error": "Snapshot not found"}, 404

    return {
        "id": str(snapshot.id),
        "name": snapshot.name,
        "speech_count": snapshot.speech_count,
        "analysis_data": snapshot.analysis_data,
        "summary": snapshot.summary,
        "created_at": snapshot.created_at.isoformat(),
    }


@router.post("/create")
async def create_snapshot(db: AsyncSession = Depends(get_db)):
    """手动创建快照"""
    # 统计当前数据
    speech_count = (await db.execute(select(func.count(Speech.id)))).scalar()

    # 获取分析汇总
    topics_result = await db.execute(
        select(Topic.topic_name, func.count(Topic.id).label("count"))
        .group_by(Topic.topic_name)
        .order_by(func.count(Topic.id).desc())
        .limit(50)
    )
    top_topics = [{"topic": r[0], "count": r[1]} for r in topics_result]

    sentiments_result = await db.execute(
        select(Sentiment.sentiment_label, func.count(Sentiment.id).label("count"))
        .group_by(Sentiment.sentiment_label)
    )
    sentiment_summary = {r[0]: r[1] for r in sentiments_result}

    analysis_data = {
        "top_topics": top_topics,
        "sentiment_summary": sentiment_summary,
        "total_speeches": speech_count,
    }

    snapshot = Snapshot(
        name=f"快照 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        description="自动生成的阶段性分析快照",
        speech_count=speech_count,
        analysis_data=analysis_data,
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)

    return {"id": str(snapshot.id), "name": snapshot.name, "created_at": snapshot.created_at.isoformat()}
