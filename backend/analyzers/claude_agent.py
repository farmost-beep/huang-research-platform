"""Claude API 分析引擎 — 黄仁勋演讲深度分析"""
import json
import logging
from datetime import datetime

from config import settings
from database.models import Speech, Topic, Sentiment, Narrative

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """使用 Claude API 对黄仁勋演讲进行多维度分析"""

    def __init__(self):
        self.client = None
        if settings.claude_api_key:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=settings.claude_api_key,
                base_url="https://api.anthropic.com/v1",
            )

    async def analyze_pending(self) -> dict:
        """分析所有未分析的演讲"""
        from database.connection import async_session
        from sqlalchemy import select, func

        async with async_session() as session:
            # 查找还没有分析结果的演讲
            subq = select(Topic.speech_id).distinct()
            result = await session.execute(
                select(Speech).where(Speech.id.not_in(subq))
                .order_by(Speech.date.desc())
                .limit(settings.analysis_batch_size)
            )
            speeches = result.scalars().all()

            if not speeches:
                logger.info("没有待分析的演讲")
                return {"analyzed": 0}

            analyzed = 0
            for speech in speeches:
                success = await self._analyze_speech(session, speech)
                if success:
                    analyzed += 1

            await session.commit()
            logger.info(f"已分析 {analyzed} 篇演讲")
            return {"analyzed": analyzed, "total": len(speeches)}

    async def _analyze_speech(self, session, speech: Speech) -> bool:
        """分析单篇演讲"""
        try:
            text = speech.processed_text or speech.raw_text
            if len(text) < 100:
                logger.warning(f"文本过短，跳过分析: {speech.title}")
                return False

            # 如果文本是占位标记，跳过
            if text.startswith("[转录待采集]") or text.startswith("[待采集"):
                logger.info(f"占位记录，跳过分析: {speech.title}")
                return False

            # 使用 Claude API 进行分析
            if self.client:
                analysis = await self._call_claude(text, speech.title, speech.date)
            else:
                # 无 API key 时用规则分析
                analysis = self._rule_based_analysis(text, speech.title)

            # 保存主题
            for topic_data in analysis.get("topics", []):
                topic = Topic(
                    speech_id=speech.id,
                    topic_name=topic_data["name"],
                    relevance_score=topic_data.get("score", 0.5),
                    keywords=topic_data.get("keywords", []),
                    summary=topic_data.get("summary", ""),
                )
                session.add(topic)

            # 保存情感
            for sent_data in analysis.get("sentiments", []):
                sentiment = Sentiment(
                    speech_id=speech.id,
                    segment=sent_data.get("segment", ""),
                    sentiment_label=sent_data.get("label", "neutral"),
                    confidence=sent_data.get("confidence", 0.5),
                    text_snippet=sent_data.get("snippet", ""),
                )
                session.add(sentiment)

            # 保存叙事
            for narr_data in analysis.get("narratives", []):
                narrative = Narrative(
                    speech_id=speech.id,
                    narrative_name=narr_data["name"],
                    category=narr_data.get("category", "general"),
                    context=narr_data.get("context", ""),
                    significance=narr_data.get("significance", 0.5),
                )
                session.add(narrative)

            return True

        except Exception as e:
            logger.error(f"分析失败 {speech.title}: {e}")
            return False

    async def _call_claude(self, text: str, title: str, date: datetime) -> dict:
        """调用 Claude API 分析演讲"""
        prompt = f"""You are an expert analyst studying Jensen Huang, CEO of NVIDIA.
Analyze the following speech/statement and return JSON with:
1. topics: key topics discussed (name, relevance_score 0-1, keywords[], summary)
2. sentiments: overall sentiment segments (segment, label, confidence, snippet)
3. narratives: recurring narratives/narratives used (name, category in [metaphor, prediction, principle, strategy, vision], context, significance 0-1)

Speech title: {title}
Date: {date.strftime('%Y-%m-%d')}

Text:
{text[:8000]}

Return ONLY valid JSON with no explanation."""

        response = await self.client.chat.completions.create(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def _rule_based_analysis(self, text: str, title: str) -> dict:
        """无 API key 时的关键词规则分析"""
        text_lower = text.lower()

        # 主题关键词映射
        topic_keywords = {
            "AI & Deep Learning": ["deep learning", "artificial intelligence", "neural network", "transformer", "llm", "large language model", "gpt"],
            "Data Center": ["data center", "hyperscale", "cloud", "inference", "training"],
            "Autonomous Vehicles": ["autonomous", "self-driving", "drive", "robotaxi"],
            "Gaming": ["gaming", "game", "rtx", "graphics", "render"],
            "CUDA & Ecosystem": ["cuda", "ecosystem", "developer", "platform", "accelerated computing"],
            "Physical AI / Robotics": ["robot", "physical ai", "embodied", "omniverse", "digital twin"],
            "Geopolitics & Supply Chain": ["export control", "supply chain", "tariff", "china", "regulation"],
            "Healthcare & Life Sciences": ["healthcare", "drug discovery", "genomics", "medical"],
            "Industrial & Manufacturing": ["manufacturing", "industrial", "factory", "automation"],
        }

        topics = []
        for topic_name, keywords in topic_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                score = min(len(matches) / 5, 1.0)
                topics.append({
                    "name": topic_name,
                    "score": round(score, 2),
                    "keywords": matches[:10],
                    "summary": f"演讲涉及 {topic_name}，提及关键词: {', '.join(matches[:5])}",
                })

        # 情感分析（简单规则）
        sentiment_words = {
            "positive": ["excited", "amazing", "incredible", "great", "breakthrough", "revolutionary", "opportunity", "growth"],
            "cautious": ["challenge", "difficult", "careful", "uncertain", "complex", "but"],
            "negative": ["risk", "concern", "limitation", "problem", "issue"],
        }

        sentiments = []
        for label, words in sentiment_words.items():
            for word in words:
                if word in text_lower:
                    sentiments.append({
                        "segment": "full_text",
                        "label": label,
                        "confidence": 0.6,
                        "snippet": f"提及 '{word}'",
                    })
                    break

        if not sentiments:
            sentiments.append({"segment": "full_text", "label": "neutral", "confidence": 0.8, "snippet": "中性"})

        return {
            "topics": topics[:8],
            "sentiments": sentiments[:5],
            "narratives": [],
        }
