import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class Speech(Base):
    __tablename__ = "speeches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    source_type = Column(String(50), nullable=False, index=True)  # keynote, earnings, interview, conference, social
    source_url = Column(String(1000))
    event_name = Column(String(300))  # e.g. "GTC 2024", "Q4 FY2025 Earnings Call"
    raw_text = Column(Text, nullable=False)
    processed_text = Column(Text)
    word_count = Column(Integer, default=0)
    language = Column(String(10), default="en")
    embedding = Column(Vector(1536), nullable=True)  # pgvector
    custom_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    topics = relationship("Topic", back_populates="speech", cascade="all, delete-orphan")
    sentiments = relationship("Sentiment", back_populates="speech", cascade="all, delete-orphan")
    narratives = relationship("Narrative", back_populates="speech", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "analysis_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    speech_id = Column(UUID(as_uuid=True), ForeignKey("speeches.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_name = Column(String(200), nullable=False)
    relevance_score = Column(Float, default=0.0)
    keywords = Column(JSON, default=list)  # ["AI", "datacenter", ...]
    summary = Column(Text)

    speech = relationship("Speech", back_populates="topics")


class Sentiment(Base):
    __tablename__ = "analysis_sentiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    speech_id = Column(UUID(as_uuid=True), ForeignKey("speeches.id", ondelete="CASCADE"), nullable=False, index=True)
    segment = Column(String(200))
    sentiment_label = Column(String(20), nullable=False)  # positive, negative, neutral, excited, cautious
    confidence = Column(Float, default=0.0)
    text_snippet = Column(Text)

    speech = relationship("Speech", back_populates="sentiments")


class Narrative(Base):
    __tablename__ = "analysis_narratives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    speech_id = Column(UUID(as_uuid=True), ForeignKey("speeches.id", ondelete="CASCADE"), nullable=True, index=True)
    narrative_name = Column(String(300), nullable=False)
    category = Column(String(100))  # metaphor, prediction, principle, strategy
    context = Column(Text)
    significance = Column(Float, default=0.0)

    speech = relationship("Speech", back_populates="narratives")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    speech_count = Column(Integer, default=0)
    analysis_data = Column(JSON, default=dict)  # Full analysis state at snapshot time
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class CompanyMetric(Base):
    __tablename__ = "company_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, nullable=False, index=True)
    revenue = Column(Float)  # quarterly revenue in billions
    eps = Column(Float)  # earnings per share
    stock_price = Column(Float)  # closing price
    market_cap = Column(Float)  # in billions
    segment_revenue = Column(JSON)  # {"data_center": 18.4, "gaming": 2.5, ...}
    product_launches = Column(JSON, default=list)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
