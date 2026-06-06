from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import Speech, Topic, Sentiment, Narrative

router = APIRouter()


@router.get("/")
async def list_speeches(
    source_type: Optional[str] = None,
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Speech).order_by(Speech.date.desc())

    if source_type:
        query = query.where(Speech.source_type == source_type)
    if year:
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        query = query.where(Speech.date >= start, Speech.date < end)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    speeches = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": str(s.id),
                "title": s.title,
                "date": s.date.isoformat(),
                "source_type": s.source_type,
                "event_name": s.event_name,
                "source_url": s.source_url,
                "word_count": s.word_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in speeches
        ],
    }


@router.get("/sources")
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Speech.source_type, func.count(Speech.id).label("count"))
        .group_by(Speech.source_type)
        .order_by(func.count(Speech.id).desc())
    )
    return [{"source": row[0], "count": row[1]} for row in result]


@router.get("/{speech_id}")
async def get_speech(speech_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Speech).where(Speech.id == speech_id))
    speech = result.scalar_one_or_none()
    if not speech:
        return {"error": "Speech not found"}, 404

    # 获取关联分析
    topics_r = await db.execute(select(Topic).where(Topic.speech_id == speech.id))
    sents_r = await db.execute(select(Sentiment).where(Sentiment.speech_id == speech.id))
    narrs_r = await db.execute(select(Narrative).where(Narrative.speech_id == speech.id))

    return {
        "id": str(speech.id),
        "title": speech.title,
        "date": speech.date.isoformat(),
        "source_type": speech.source_type,
        "source_url": speech.source_url,
        "event_name": speech.event_name,
        "raw_text": speech.raw_text,
        "processed_text": speech.processed_text,
        "word_count": speech.word_count,
        "custom_metadata": speech.custom_metadata,
        "topics": [
            {
                "topic_name": t.topic_name,
                "relevance_score": t.relevance_score,
                "keywords": t.keywords,
            }
            for t in topics_r.scalars().all()
        ],
        "sentiments": [
            {
                "segment": s.segment,
                "label": s.sentiment_label,
                "confidence": s.confidence,
            }
            for s in sents_r.scalars().all()
        ],
        "narratives": [
            {
                "name": n.narrative_name,
                "category": n.category,
                "significance": n.significance,
            }
            for n in narrs_r.scalars().all()
        ],
    }
