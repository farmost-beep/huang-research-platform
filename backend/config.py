"""配置管理 — 黄仁勋研究平台"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库
    database_url: str = "postgresql+asyncpg://huang:huang_secret@localhost:5432/huang_research"

    # API Keys
    claude_api_key: str = ""
    youtube_api_key: str = ""

    # 分析配置
    analysis_batch_size: int = 10
    embedding_dim: int = 1536

    # ─── 调度策略（已确定） ───
    # [事件驱动] GTC 演讲 → 手动触发采集
    # [事件驱动] 财报电话会 → NVDIA IR 发布后手动触发
    # [定期] 每周自动扫描新采访/新闻
    # [定期] 每两周生成自动快照
    collection_interval_hours: int = 168       # 7天: 每周自动扫描
    analysis_interval_hours: int = 24          # 1天: 新数据尽快分析
    snapshot_interval_days: int = 14           # 2周: 定期快照

    # ─── 数据源优先级（已确定） ───
    # P0: GTC Keynote + NVIDIA 财报电话会
    # P1: 深度媒体采访 (60 Minutes, Bloomberg, CNBC, Stanford)
    # P2: 行业大会演讲 (SIGGRAPH, Computex, AI Summit)
    # P3: 社交媒体 (X/Twitter)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
