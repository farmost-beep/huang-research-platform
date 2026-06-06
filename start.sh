#!/bin/bash
# =============================================================
# 快速启动脚本 — 在你的 Mac 终端执行: bash /Users/cyingfang/web/start.sh
# =============================================================
set -e

cd /Users/cyingfang/web

echo ""
echo "=========================================="
echo "  1. 确保 PostgreSQL 已启动"
echo "=========================================="
brew services start postgresql@18 2>/dev/null || true
sleep 1

echo ""
echo "=========================================="
echo "  2. 创建数据库"
echo "=========================================="
createdb huang_research 2>/dev/null && echo "  ✅ 数据库已创建" || echo "  数据库已存在"
psql -d huang_research -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true

echo ""
echo "=========================================="
echo "  3. 安装后端依赖"
echo "=========================================="
cd backend
pip3 install -r requirements.txt -q 2>/dev/null

echo ""
echo "=========================================="
echo "  4. 灌入种子数据 + 分析"
echo "=========================================="
python3 << 'PYEOF'
import asyncio, datetime
from database.connection import engine, async_session
from database.models import Base, Speech, Topic, Sentiment, Narrative, Snapshot
from sqlalchemy import select, func

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        count = (await session.execute(select(func.count(Speech.id)))).scalar()
        if count == 0:
            print("  插入示例数据...")
            samples = [
                Speech(title="GTC 2024 Keynote — Blackwell 发布", date=datetime.datetime(2024,3,18), source_type="keynote", event_name="GTC 2024", raw_text="Jensen Huang opened GTC 2024 by declaring that generative AI has reached a tipping point. He unveiled the Blackwell GPU platform, calling it the world's most powerful chip. He emphasized that accelerated computing is the sustainable path forward and that AI factories are the new industrial revolution. Jensen stated that the iPhone moment of AI arrived years ago and now we are in the scaling phase. He discussed NVIDIA's transition from a GPU company to an AI infrastructure company, highlighting the full-stack computing approach from chips to systems to software.", processed_text="", word_count=78),
                Speech(title="Computex 2024 Keynote — AI 工业革命", date=datetime.datetime(2024,6,2), source_type="keynote", event_name="Computex 2024", raw_text="At Computex 2024 in Taipei, Jensen Huang announced the Rubin architecture for 2026 and demonstrated NVIDIA's annual cadence of new chips. He framed AI as a full-stack computing challenge and introduced the concept of 'AI factories' that process raw data into tokens. Jensen emphasized that NVIDIA is no longer just a chip company but a 'data center-scale' company. He discussed partnerships across the AI ecosystem and showcased how every industry from healthcare to manufacturing is adopting AI.", processed_text="", word_count=68),
                Speech(title="CES 2025 Keynote — 物理 AI 时代", date=datetime.datetime(2025,1,6), source_type="keynote", event_name="CES 2025", raw_text="In his CES 2025 keynote, Jensen Huang outlined the next phase of AI: physical AI and robotics. He announced NVIDIA's entry into autonomous driving with new automotive partnerships. Jensen argued that the next wave of AI will be physical — robots, autonomous vehicles, and digital twins in Omniverse. He demonstrated real-world applications of AI in manufacturing, logistics, and healthcare, positioning NVIDIA as the operating system of the physical AI economy.", processed_text="", word_count=68),
                Speech(title="Q1 FY2026 财报电话会", date=datetime.datetime(2025,5,28), source_type="earnings", event_name="NVIDIA Q1 FY2026 Earnings Call", raw_text="Jensen reported record quarterly revenue driven by Hopper and Blackwell GPU demand. He noted that sovereign AI initiatives are accelerating globally, with countries investing in their own AI infrastructure. Jensen highlighted that inference workloads are growing rapidly as AI applications scale, and that NVIDIA's full-stack platform gives it a unique competitive advantage. He expressed confidence in the company's ability to maintain growth amid increasing competition and geopolitical challenges.", processed_text="", word_count=60),
                Speech(title="Stanford GSB 访谈 — 领导力哲学", date=datetime.datetime(2024,3,14), source_type="interview", event_name="Stanford GSB Viewpoint", raw_text="In a fireside chat at Stanford Graduate School of Business, Jensen shared his leadership philosophy. He described his management style as 'flat and transparent,' with no direct reports and an open-door policy. Jensen talked about the concept of 'zero-billion dollar markets' — pursuing ideas that seem impossible before they become essential. He emphasized intellectual honesty over ego, the importance of staying close to the technology, and why NVIDIA has survived multiple near-death experiences.", processed_text="", word_count=68),
                Speech(title="GTC 2023 Keynote — AI 的 iPhone 时刻", date=datetime.datetime(2023,3,21), source_type="keynote", event_name="GTC 2023", raw_text="Jensen Huang declared at GTC 2023 that the iPhone moment of AI has arrived. He introduced the H100 GPU and DGX Cloud service, positioning NVIDIA as the engine of the AI revolution. Jensen discussed how ChatGPT has demonstrated the power of large language models and why accelerated computing is the path forward. He emphasized NVIDIA's CUDA ecosystem moat and how the company's decade-long bet on AI is now paying off.", processed_text="", word_count=62),
                Speech(title="60 Minutes 专访 — AI 的变革力量", date=datetime.datetime(2024,12,8), source_type="interview", event_name="60 Minutes", raw_text="In a rare long-form television interview, Jensen spoke with 60 Minutes about the transformative power of AI. He discussed NVIDIA's journey from a graphics company to the world's most valuable technology company. Jensen shared personal stories about founding NVIDIA, the company's near-bankruptcy in the early days, and his management philosophy. He emphasized that AI is the most important technology of our lifetime and that NVIDIA is just getting started.", processed_text="", word_count=65),
                Speech(title="SIGGRAPH 2024 — Zuck 对谈", date=datetime.datetime(2024,7,29), source_type="conference", event_name="SIGGRAPH 2024", raw_text="At SIGGRAPH 2024, Jensen Huang and Mark Zuckerberg shared the stage for a fireside chat. They discussed the future of AI, open-source AI models, and the metaverse. Jensen emphasized that AI will revolutionize content creation and that every industry will be transformed by generative AI. He and Zuckerberg discussed their shared vision for AI-powered digital humans and the convergence of AI and graphics.", processed_text="", word_count=58),
                Speech(title="Q4 FY2025 财报电话会", date=datetime.datetime(2025,2,26), source_type="earnings", event_name="NVIDIA Q4 FY2025 Earnings Call", raw_text="NVIDIA reported exceptional quarterly results with record data center revenue. Jensen highlighted that demand for Blackwell is 'incredible' and that AI is rapidly transitioning from training to inference. He discussed the ramp of Hopper and Blackwell architectures, sovereign AI buildouts, and enterprise AI adoption. Jensen expressed optimism about NVIDIA's position in the AI infrastructure market despite export control challenges.", processed_text="", word_count=55),
            ]
            for s in samples:
                session.add(s)
            await session.commit()
            print(f"  ✅ {len(samples)} 条演讲已入库")
        else:
            print(f"  已有 {count} 条数据")

        # 运行关键词分析（无 API key 时用规则引擎）
        from analyzers.claude_agent import ClaudeAnalyzer
        analyzer = ClaudeAnalyzer()
        result = await analyzer.analyze_pending()
        print(f"  ✅ 分析完成: {result}")

        # 创建初始快照
        snap = Snapshot(name="初始快照 2026-06", description="首次数据分析快照", speech_count=(await session.execute(select(func.count(Speech.id)))).scalar(), analysis_data={"status": "initial"})
        session.add(snap)
        await session.commit()
        print(f"  ✅ 初始快照已创建")

asyncio.run(init())
PYEOF

echo ""
echo "=========================================="
echo "  5. 启动后端 API 服务"
echo "=========================================="
# 杀掉旧进程
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/uvicorn.log 2>&1 &
echo "  后端 PID: $!"
sleep 2
echo "  ✅ 后端已启动: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"

echo ""
echo "=========================================="
echo "  🎉 全部就绪！请刷新 http://localhost:3000"
echo "=========================================="
echo ""
echo "  停止后端: kill \$(lsof -ti:8000)"
echo "  查看日志: tail -f /tmp/uvicorn.log"
echo "=========================================="
