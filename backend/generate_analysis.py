"""
生成主题分析数据（topics, sentiments, keywords）
基于每条演讲的内容、标题和类型，分配主题和情感分析
"""

import uuid
import asyncio
import re
from collections import Counter

from database.connection import async_session
from database.models import Speech, Topic, Sentiment
from sqlalchemy import select, text


# ========== 主题词库 ==========

TOPIC_RULES = [
    (["AI", "人工智能", "artificial intelligence"], "Artificial Intelligence", 0.95),
    (["GPU", "graphics", "图形", "CUDA", "cuda"], "GPU Computing", 0.90),
    (["data center", "datacenter", "数据中心", "DGX"], "Data Center", 0.85),
    (["autonomous", "self-driving", "自动驾驶", "DRIVE", "Orin"], "Autonomous Vehicles", 0.85),
    (["robot", "robotics", "机器人", "Isaac"], "Robotics", 0.80),
    (["Blackwell", "blackwell"], "Blackwell Architecture", 0.95),
    (["Hopper", "H100", "hopper"], "Hopper Architecture", 0.90),
    (["Ampere", "A100", "ampere"], "Ampere Architecture", 0.90),
    (["Grace", "grace"], "Grace CPU", 0.85),
    (["Rubin", "rubin"], "Rubin Architecture", 0.95),
    (["RTX", "ray tracing", "光线追踪"], "Real-Time Graphics", 0.80),
    (["transformer", "Transformer", "大模型", "LLM", "GPT"], "Large Language Models", 0.85),
    (["accelerated computing", "加速计算"], "Accelerated Computing", 0.85),
    (["healthcare", "医疗", "Clara", "clara"], "Healthcare AI", 0.75),
    (["manufacturing", "制造", "factory", "工厂", "工业"], "Industrial AI", 0.80),
    (["startup", "创业", "zero-billion", "0亿美元"], "Entrepreneurship", 0.85),
    (["leadership", "领导力", "management", "管理", "flat"], "Leadership & Management", 0.85),
    (["education", "教育", "university", "大学", "毕业"], "Education & Career", 0.70),
    (["sovereign AI", "主权", "主权AI", "nation"], "Sovereign AI", 0.80),
    (["physical AI", "物理AI", "physical"], "Physical AI", 0.85),
    (["chip", "架构", "architecture", "transistor", "晶体管", "semiconductor"], "Chip Architecture", 0.80),
    (["omniverse", "Omniverse", "digital twin", "数字孪生"], "Omniverse & Digital Twins", 0.80),
    (["automotive", "汽车", "vehicle"], "Automotive", 0.75),
    (["gaming", "游戏", "gamer"], "Gaming", 0.70),
    (["cloud", "云"], "Cloud Computing", 0.65),
    (["sustainable", "可持续", "energy"], "Sustainable Computing", 0.70),
    (["inference", "推理", "training", "训练"], "AI Inference & Training", 0.80),
    (["HPC", "supercomputer", "超级计算", "高性能"], "High Performance Computing", 0.85),
    (["edge", "IoT"], "Edge AI", 0.70),
    (["Vision", "vision", "computer vision"], "Computer Vision", 0.75),
    (["generative", "生成式", "生成"], "Generative AI", 0.85),
    (["agent", "Agent", "智能体"], "AI Agents", 0.80),
]

SOURCE_TOPICS = {
    "keynote": [("Product Launch", 0.70), ("Technology Vision", 0.85)],
    "earnings": [("Financial Performance", 0.90), ("Business Strategy", 0.85), ("Market Outlook", 0.80)],
    "conference": [("Industry Collaboration", 0.75), ("Technology Vision", 0.80)],
    "interview": [("Leadership Insights", 0.80), ("Company Culture", 0.75), ("Personal Journey", 0.70)],
    "speech": [("Motivational", 0.70), ("Career Advice", 0.75)],
    "biography": [("Personal History", 0.90), ("Company History", 0.85)],
}


def match_topics(title, raw_text, source_type):
    """基于内容匹配分配主题"""
    content = (title + " " + (raw_text or "")).lower()
    topics = []

    for keywords, topic_name, score in TOPIC_RULES:
        for kw in keywords:
            if kw.lower() in content:
                topics.append((topic_name, score))
                break

    # 添加演讲类型通用主题
    for topic_name, score in SOURCE_TOPICS.get(source_type, []):
        if not any(t[0] == topic_name for t in topics):
            topics.append((topic_name, score * 0.9))

    # 去重并限制最多5个
    seen = set()
    unique = []
    for name, score in topics:
        if name not in seen:
            seen.add(name)
            unique.append((name, score))
    topics = unique[:5]

    if not topics:
        topics.append(("Technology & Innovation", 0.60))

    return topics


def extract_keywords(title, raw_text, source_type):
    """从内容中提取关键词"""
    content = title + " " + (raw_text or "")

    keyword_lib = {
        "keynote": ["GTC", "keynote", "NVIDIA", "AI", "GPU", "加速计算", "数据中心"],
        "earnings": ["财报", "营收", "增长", "Blackwell", "Hopper", "需求", "NVIDIA"],
        "conference": ["合作", "AI", "创新", "NVIDIA", "生态", "未来"],
        "interview": ["访谈", "领导力", "创业", "AI", "未来", "Jensen Huang"],
        "speech": ["毕业典礼", "演讲", "AI", "未来", "创新", "Jensen Huang"],
        "biography": ["黄仁勋", "NVIDIA", "创业", "历程", "台湾", "Jensen Huang"],
    }

    keywords = keyword_lib.get(source_type, ["AI", "NVIDIA", "创新"])

    eng_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
    for w in eng_words[:5]:
        if w not in keywords and len(w) > 2 and w.lower() not in ['the', 'this', 'that', 'with', 'from']:
            keywords.append(w)

    return keywords[:8]


def analyze_sentiment(text, source_type):
    """简单基于规则的情感分析"""
    if not text:
        return []

    text_lower = text.lower()

    seg_names = [
        ("开场", 0, 0.15),
        ("核心内容", 0.15, 0.75),
        ("总结展望", 0.75, 1.0),
    ]

    sentiment_kw = {
        "positive": [
            "amazing", "incredible", "exciting", "breakthrough", "revolutionary",
            "great", "fantastic", "extraordinary", "remarkable", "里程碑", "突破",
            "激动", "前所未有", "伟大", "创新", "颠覆",
        ],
        "negative": [
            "difficult", "challenging", "hard", "tough", "struggle", "危机",
            "困难", "挑战", "濒临", "破产", "失败", "艰难",
        ],
        "neutral": [
            "interesting", "important", "significant", "未来", "计划", "战略",
            "发展", "增长", "机会", "趋势",
        ],
    }

    sentiments = []
    for seg_name, start_pct, end_pct in seg_names:
        seg_len = len(text)
        seg_start = int(seg_len * start_pct)
        seg_end = int(seg_len * end_pct)
        seg_text = text_lower[seg_start:seg_end]

        scores = {}
        for label, keywords in sentiment_kw.items():
            count = sum(1 for kw in keywords if kw.lower() in seg_text)
            if count > 0:
                scores[label] = scores.get(label, 0) + count

        if scores:
            dominant = max(scores, key=scores.get)
            confidence = min(0.5 + scores[dominant] * 0.1, 0.95)
        else:
            # source_type-based default
            if source_type in ("interview", "speech", "biography"):
                dominant = "neutral"
            elif source_type == "earnings":
                dominant = "positive"
            else:
                dominant = "positive"
            confidence = 0.55

        sentiments.append({
            "segment": seg_name,
            "label": dominant,
            "confidence": round(confidence, 2),
        })

    return sentiments


async def run():
    async with async_session() as db:
        # 清空旧数据
        await db.execute(text("DELETE FROM analysis_topics"))
        await db.execute(text("DELETE FROM analysis_sentiments"))
        await db.commit()
        print("旧分析数据已清空")

        # 获取所有演讲
        result = await db.execute(select(Speech))
        speeches = result.scalars().all()

        topic_count = 0
        sentiment_count = 0

        for speech in speeches:
            title = speech.title or ""
            raw_text = speech.raw_text or ""
            source_type = speech.source_type or ""

            # 分配主题
            topics = match_topics(title, raw_text, source_type)
            kw = extract_keywords(title, raw_text, source_type)

            for topic_name, score in topics:
                topic = Topic(
                    id=str(uuid.uuid4()),
                    speech_id=speech.id,
                    topic_name=topic_name,
                    relevance_score=score,
                    keywords=kw,
                )
                db.add(topic)
                topic_count += 1

            # 情感分析
            sentiments = analyze_sentiment(raw_text, source_type)
            for s in sentiments:
                sentiment = Sentiment(
                    id=str(uuid.uuid4()),
                    speech_id=speech.id,
                    segment=s["segment"],
                    sentiment_label=s["label"],
                    confidence=s["confidence"],
                    text_snippet=raw_text[:80] if raw_text else "",
                )
                db.add(sentiment)
                sentiment_count += 1

        await db.commit()
        print(f"已插入 {topic_count} 个主题分析（{len(speeches)} 篇演讲）")
        print(f"已插入 {sentiment_count} 条情感分析")

        # 统计主题分布
        result = await db.execute(
            select(Topic.topic_name, Topic.relevance_score)
        )
        topic_freq = Counter()
        topic_score_sum = {}
        for row in result:
            name = row[0]
            score = row[1] or 0
            topic_freq[name] += 1
            topic_score_sum[name] = topic_score_sum.get(name, 0) + score

        print("\n主题分布 Top 10:")
        for name, count in topic_freq.most_common(10):
            avg = topic_score_sum[name] / count
            print(f"  {name:<30} {count:>3}次  avg_score={avg:.2f}")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
