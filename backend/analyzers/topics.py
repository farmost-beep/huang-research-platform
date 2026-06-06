"""主题分析工具"""
from collections import Counter
from typing import List


class TopicAnalyzer:
    """提取和聚合演讲主题的工具方法"""

    @staticmethod
    def extract_keywords(text: str, top_n: int = 50) -> List[dict]:
        """基于 TF 提取关键词"""
        import jieba
        import jieba.analyse
        import re

        # 如果是英文文本
        if re.match(r'^[a-zA-Z\s.,!?]+$', text[:200]):
            words = text.lower().split()
            # 过滤停用词
            stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                        "of", "with", "by", "is", "are", "was", "were", "be", "been",
                        "this", "that", "it", "its", "we", "our", "you", "they", "their",
                        "i", "my", "me", "do", "does", "did", "will", "would", "can", "could",
                        "have", "has", "had", "not", "no", "so", "very", "just", "about"}
            words = [w for w in words if w not in stopwords and len(w) > 2]
            freq = Counter(words).most_common(top_n)
            return [{"word": w, "freq": c} for w, c in freq]

        # 中文文本
        keywords = jieba.analyse.extract_tags(text, topK=top_n, withWeight=True)
        return [{"word": w, "weight": round(float(wt), 4)} for w, wt in keywords]
