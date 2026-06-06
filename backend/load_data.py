#!/usr/bin/env python3
"""全面数据灌入脚本：黄仁勋生平 + 全部演讲 + 财报数据 + 叙事框架（含信源链接）"""
import asyncio, datetime
from database.connection import engine, async_session
from database.models import Base, Speech, Topic, Sentiment, Narrative, Snapshot, CompanyMetric
from sqlalchemy import select, func, delete


async def reload():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        for table in [Topic, Sentiment, Narrative, Snapshot, CompanyMetric]:
            await session.execute(delete(table))
        await session.execute(delete(Speech))
        await session.commit()
        print("旧数据已清空")

        # ============ 传记 ============
        bios = [
            Speech(title="黄仁勋传记（一）：台南出生到移民美国", date=datetime.datetime(1963,2,17),
                source_type="biography", event_name="人生故事",
                source_url="https://en.wikipedia.org/wiki/Jensen_Huang",
                raw_text="黄仁勋1963年2月17日出生于台湾台南市，祖籍浙江。父亲黄兴泰是化学工程师，母亲罗采秀是小学教师。5岁时全家搬到泰国曼谷。1972年9岁的黄仁勋和哥哥被送到美国肯塔基州的奥奈达浸信会学院（Oneida Baptist Institute），这实际上是一所问题少年感化院。他在这里打扫厕所，学会了生存与适应。他后来说这段经历是我最好的老师。1974年父母移民美国，全家在俄勒冈团聚。入读阿罗哈高中，跳级学习。15岁获全美青少年乒乓球双打季军。在丹尼餐厅打工做服务员。16岁高中毕业。",
                word_count=300),
            Speech(title="黄仁勋传记（二）：大学到创立NVIDIA", date=datetime.datetime(1984,6,1),
                source_type="biography", event_name="人生故事",
                source_url="https://en.wikipedia.org/wiki/Jensen_Huang",
                raw_text="1984年获得俄勒冈州立大学电子工程学士学位。毕业后加入AMD担任微处理器设计师。1985年跳槽至LSI Logic，从工程师主动转到销售部，8年做到董事。期间在斯坦福大学攻读夜校，1992年获电子工程硕士学位。1993年2月17日30岁生日，与克里斯马拉科夫斯基和柯蒂斯普里姆在丹尼餐厅凑了4万美元创立NVIDIA。公司名字来自拉丁语invidia（嫉妒）。",
                word_count=220),
            Speech(title="黄仁勋传记（三）：濒临破产到逆袭称王", date=datetime.datetime(1997,8,1),
                source_type="biography", event_name="人生故事",
                source_url="https://en.wikipedia.org/wiki/NVIDIA",
                raw_text="1995年NV1失败，公司从100多人裁到30多人。1996年与世嘉合作NV2再次失败。黄仁勋坦诚向世嘉CEO承认困境，要回700万美元定金让公司多活6个月。1997年RIVA 128（NV3）出货100万片一战成名。1999年GeForce 256全球首款GPU，同年上市。2000年收购3Dfx。2006年推出CUDA，市值一度跌至10亿美元，但成为AI基石。",
                word_count=220),
        ]
        for s in bios:
            session.add(s)
        await session.commit()
        print("已插入 3 篇传记")

        # ============ 全部主题演讲 ============
        speeches = [
            # GTC Keynotes (全部附 YouTube 链接)
            Speech(title="GTC 2018 Keynote — NVIDIA的AI新纪元", date=datetime.datetime(2018,3,27),
                source_type="keynote", event_name="GTC 2018",
                source_url="https://www.youtube.com/watch?v=KkqwydFwrxE",
                raw_text="Jensen Huang opened GTC 2018 with a major emphasis on AI. He announced the NVIDIA T4 GPU for AI inference and introduced DGX-2 the world's most powerful AI system combining 16 GPUs. He demonstrated real-time AI video translation. He declared that AI is the most powerful technology force of our time."),
            Speech(title="GTC 2019 Keynote — 数据中心新时代", date=datetime.datetime(2019,3,18),
                source_type="keynote", event_name="GTC 2019",
                source_url="https://www.youtube.com/watch?v=HlKiSJ8F_aE",
                raw_text="Jensen unveiled the NVIDIA T4 inference platform and announced partnerships with Toyota for autonomous driving. He introduced the ORIN system-on-a-chip for self-driving cars. He said every data center will be accelerated."),
            Speech(title="GTC 2020 Keynote — Ampere A100发布", date=datetime.datetime(2020,5,14),
                source_type="keynote", event_name="GTC 2020",
                source_url="https://www.youtube.com/watch?v=w1d4oO0CxmI",
                raw_text="Delivered from his kitchen due to the pandemic. Jensen unveiled A100 GPU with 54 billion transistors based on Ampere architecture. He called it the most important GPU in NVIDIA's history. He announced DGX A100 and discussed AI for COVID-19 drug discovery. He announced the Mellanox acquisition."),
            Speech(title="GTC 2021 Keynote — Grace CPU与三芯片战略", date=datetime.datetime(2021,4,12),
                source_type="keynote", event_name="GTC 2021",
                source_url="https://www.youtube.com/watch?v=eA4-2JwwnN4",
                raw_text="Jensen unveiled NVIDIA's three-chip strategy: GPU (Ampere), CPU (Grace), and DPU (BlueField). He announced Grace CPU named after Grace Hopper. He introduced the vision of AI factories processing raw data into intelligence. He discussed NVIDIA's transformation to a data center-scale computing company."),
            Speech(title="GTC 2022 Keynote — Hopper H100发布", date=datetime.datetime(2022,3,22),
                source_type="keynote", event_name="GTC 2022",
                source_url="https://www.youtube.com/watch?v=DiI3n1HZZYM",
                raw_text="Jensen unveiled Hopper GPU architecture. H100 features 80 billion transistors built on TSMC 4N. He announced Quantum-2 InfiniBand for connecting thousands of GPUs. He discussed the transition from training to inference and introduced Omniverse for the metaverse."),
            Speech(title="GTC 2023 Keynote — AI的iPhone时刻", date=datetime.datetime(2023,3,21),
                source_type="keynote", event_name="GTC 2023",
                source_url="https://www.youtube.com/watch?v=_Ff2CqL02M0",
                raw_text="Jensen declared the iPhone moment of AI has arrived. He introduced H100 GPU and DGX Cloud. He announced partnerships with Microsoft, Google and Oracle. He said over 4 million developers now use CUDA. He showcased ChatGPT demonstrating the power of large language models."),
            Speech(title="GTC 2024 Keynote — Blackwell 2080亿晶体管", date=datetime.datetime(2024,3,18),
                source_type="keynote", event_name="GTC 2024",
                source_url="https://www.youtube.com/watch?v=Y2FgD5EN5Ig",
                raw_text="GTC 2024 was Jensen's most anticipated keynote. He unveiled Blackwell GPU with 208 billion transistors combining two dies with 10 TB/s interconnect. He said generative AI has reached a tipping point and AI factories are the new industrial revolution. The keynote drew millions of viewers worldwide."),
            # Computex
            Speech(title="Computex 2023 Keynote — 台湾AI供应链", date=datetime.datetime(2023,5,28),
                source_type="keynote", event_name="Computex 2023",
                source_url="https://www.youtube.com/watch?v=4JxN7UjtMlY",
                raw_text="At Computex 2023 in Taipei, Jensen showcased accelerated computing and generative AI. He emphasized Taiwan is at the center of the AI supply chain. He demonstrated real-time AI applications and announced new manufacturing partnerships."),
            Speech(title="Computex 2024 Keynote — Rubin架构", date=datetime.datetime(2024,6,2),
                source_type="keynote", event_name="Computex 2024",
                source_url="https://www.youtube.com/watch?v=8B6p9ty1FLE",
                raw_text="Jensen announced Rubin architecture for 2026 and NVIDIA's annual chip cadence. He said NVIDIA is a data center-scale company. He announced GPU and CPU roadmap through 2027."),
            Speech(title="Computex 2025 Keynote — AI超级计算机", date=datetime.datetime(2025,5,19),
                source_type="keynote", event_name="Computex 2025",
                source_url="https://www.youtube.com/watch?v=nNbjoe47FqQ",
                raw_text="Jensen announced a new AI supercomputer for Taiwan. He discussed sovereign AI and called for every nation to build its own AI infrastructure. He said AI is as much a national asset as any resource."),
            # CES
            Speech(title="CES 2025 Keynote — 物理AI与机器人", date=datetime.datetime(2025,1,6),
                source_type="keynote", event_name="CES 2025",
                source_url="https://www.youtube.com/watch?v=Gz1Cj2ZLCcE",
                raw_text="Jensen outlined the next phase: physical AI and robotics. He announced NVIDIAs entry into autonomous driving. He said the next wave of AI will be physical. He positioned NVIDIA as the operating system of the physical AI economy."),
            # 采访
            Speech(title="Stanford GSB — 零亿美元市场与领导力", date=datetime.datetime(2024,3,14),
                source_type="interview", event_name="Stanford GSB",
                source_url="https://www.youtube.com/watch?v=OZ2cy0NNxbs",
                raw_text="At Stanford GSB, Jensen shared his leadership philosophy: flat organization, no direct reports, no 1-on-1 meetings. He described zero-billion dollar markets: pursue ideas that seem impossible before they become essential. He said unless you can tolerate failure you will never innovate."),
            Speech(title="60 Minutes — AI最伟大的技术", date=datetime.datetime(2024,12,8),
                source_type="interview", event_name="60 Minutes",
                source_url="https://www.cbsnews.com/60-minutes/",
                raw_text="In a rare long-form TV interview, Jensen spoke about AI's transformative power. He shared NVIDIA's journey from graphics to the world's most valuable company. He said AI is the most important technology of our lifetime and we are only at the beginning."),
            Speech(title="Joe Rogan播客 — 坦诚3小时对话", date=datetime.datetime(2025,5,15),
                source_type="interview", event_name="Joe Rogan Experience",
                source_url="https://www.youtube.com/watch?v=5U0LAhMhCac",
                raw_text="In a rare 3-hour podcast, Jensen shared his life story. He still feels NVIDIA is 30 days from going out of business. He works 7 days a week in constant anxiety. He said the feeling of vulnerability never leaves you. He discussed being a dishwasher at Denny's and cleaning toilets at Oneida."),
            # 毕业典礼
            Speech(title="NTU毕业典礼 — 奔跑吧别走", date=datetime.datetime(2023,5,27),
                source_type="speech", event_name="NTU Commencement",
                source_url="https://www.youtube.com/watch?v=LMhqnI6KX0A",
                raw_text="At National Taiwan University commencement, Jensen advised: Run dont walk. Either you are running for food or running from becoming food. Either way run. He said you can use many words to describe me but resilient must be at the top."),
            Speech(title="Caltech毕业典礼 — 追求零亿美元市场", date=datetime.datetime(2024,6,14),
                source_type="speech", event_name="Caltech Commencement",
                source_url="https://www.youtube.com/watch?v=Yf5mhR_R5Qk",
                raw_text="At Caltech commencement, Jensen told graduates to pursue zero-billion dollar markets. He said great ideas are fragile and need to be protected. CUDA was a zero-billion dollar bet that became NVIDIAs greatest asset."),
            Speech(title="CMU毕业典礼 — 最强工具的时代", date=datetime.datetime(2026,5,11),
                source_type="speech", event_name="CMU Commencement",
                source_url="https://www.youtube.com/watch?v=VpPx2QBK4Cc",
                raw_text="At Carnegie Mellon 2026 commencement, Jensen said no generation has entered the world with more powerful tools or greater opportunities than you. This is your moment to shape what comes next. So run dont walk."),
            # 财报
            Speech(title="Q1 FY2024财报 — AI新纪元开启", date=datetime.datetime(2023,5,24),
                source_type="earnings", event_name="NVIDIA Q1 FY2024",
                source_url="https://investor.nvidia.com/financial-info/quarterly-results/default.aspx",
                raw_text="Record data center revenue of $4.28 billion driven by AI demand. Jensen said a new computing era has begun. Companies worldwide are racing to adopt generative AI."),
            Speech(title="Q2 FY2024财报 — 营收暴增101%", date=datetime.datetime(2023,8,23),
                source_type="earnings", event_name="NVIDIA Q2 FY2024",
                source_url="https://investor.nvidia.com/financial-info/quarterly-results/default.aspx",
                raw_text="Record quarterly revenue of $13.5 billion up 101% YoY. Data center revenue $10.3 billion up 171%. Jensen said companies are transitioning to accelerated computing."),
            Speech(title="Q4 FY2025财报 — Blackwell需求令人难以置信", date=datetime.datetime(2025,2,26),
                source_type="earnings", event_name="NVIDIA Q4 FY2025",
                source_url="https://investor.nvidia.com/financial-info/quarterly-results/default.aspx",
                raw_text="Exceptional quarterly results. Jensen said demand for Blackwell is incredible. He discussed transition from training to inference and sovereign AI buildouts worldwide."),
            Speech(title="Q1 FY2026财报 — 主权AI加速", date=datetime.datetime(2025,5,28),
                source_type="earnings", event_name="NVIDIA Q1 FY2026",
                source_url="https://investor.nvidia.com/financial-info/quarterly-results/default.aspx",
                raw_text="Record revenue driven by Hopper and Blackwell demand. Sovereign AI initiatives accelerating globally. Inference workloads growing rapidly as AI applications scale."),
            # 行业大会
            Speech(title="SIGGRAPH 2023 — AI与图形融合", date=datetime.datetime(2023,8,8),
                source_type="conference", event_name="SIGGRAPH 2023",
                source_url="https://www.youtube.com/watch?v=coCBlngJ3hI",
                raw_text="Jensen discussed the convergence of AI and computer graphics. He showcased real-time ray tracing and AI-powered graphics. He said AI is revolutionizing content creation."),
            Speech(title="SIGGRAPH 2024 — 与扎克伯格历史对谈", date=datetime.datetime(2024,7,29),
                source_type="conference", event_name="SIGGRAPH 2024",
                source_url="https://www.youtube.com/watch?v=1o0ZaCwkO0A",
                raw_text="Jensen and Mark Zuckerberg shared the stage for a historic fireside chat. They discussed the future of AI open-source models and the metaverse. Jensen said AI will revolutionize content creation."),
            Speech(title="World Government Summit 2024 — AI治理", date=datetime.datetime(2024,2,12),
                source_type="conference", event_name="World Government Summit",
                source_url="https://www.worldgovernmentsummit.org/",
                raw_text="At the World Government Summit in Dubai Jensen discussed AI governance and regulation. He called on governments to invest in AI infrastructure. He said sovereign AI protects cultural heritage."),
        ]
        for s in speeches:
            session.add(s)
        await session.commit()
        print("已插入 " + str(len(speeches)) + " 篇演讲（全部含 source_url）")

        # ============ 财务数据 ============
        metrics = [
            CompanyMetric(date=datetime.datetime(2023,1,31), revenue=6.05, eps=0.57, stock_price=200, market_cap=500, segment_revenue={"data_center": 3.6, "gaming": 1.8}),
            CompanyMetric(date=datetime.datetime(2023,4,30), revenue=7.19, eps=0.82, stock_price=280, market_cap=700, segment_revenue={"data_center": 4.28, "gaming": 2.2}),
            CompanyMetric(date=datetime.datetime(2023,7,31), revenue=13.5, eps=2.48, stock_price=460, market_cap=1200, segment_revenue={"data_center": 10.3, "gaming": 2.4}),
            CompanyMetric(date=datetime.datetime(2023,10,31), revenue=18.1, eps=3.73, stock_price=490, market_cap=1500, segment_revenue={"data_center": 14.5, "gaming": 2.8}),
            CompanyMetric(date=datetime.datetime(2024,1,31), revenue=22.1, eps=4.93, stock_price=680, market_cap=1700, segment_revenue={"data_center": 18.4, "gaming": 2.9}),
            CompanyMetric(date=datetime.datetime(2024,4,30), revenue=26.0, eps=5.98, stock_price=880, market_cap=2200, segment_revenue={"data_center": 22.6, "gaming": 2.5}),
            CompanyMetric(date=datetime.datetime(2024,7,31), revenue=30.0, eps=6.78, stock_price=1180, market_cap=3000, segment_revenue={"data_center": 26.3, "gaming": 2.0}),
            CompanyMetric(date=datetime.datetime(2024,10,31), revenue=35.0, eps=7.85, stock_price=1400, market_cap=3600, segment_revenue={"data_center": 30.8, "gaming": 2.2}),
            CompanyMetric(date=datetime.datetime(2025,1,31), revenue=39.0, eps=8.50, stock_price=1600, market_cap=4200, segment_revenue={"data_center": 34.5, "gaming": 1.8}),
            CompanyMetric(date=datetime.datetime(2025,4,30), revenue=42.0, eps=9.20, stock_price=1750, market_cap=4600, segment_revenue={"data_center": 37.0, "gaming": 1.9}),
        ]
        for m in metrics:
            session.add(m)
        await session.commit()
        print("已插入 " + str(len(metrics)) + " 期财务数据")

        # ============ 叙事框架 ============
        narratives = [
            ("iPhone moment of AI", "metaphor"),
            ("AI factories are the new industrial revolution", "vision"),
            ("Zero-billion dollar markets", "principle"),
            ("30 days from going out of business", "principle"),
            ("Flat organization / No 1-on-1", "principle"),
            ("Run dont walk", "principle"),
            ("Intellectual honesty over ego", "principle"),
            ("Full-stack computing platform", "strategy"),
            ("Sovereign AI for every nation", "vision"),
            ("Physical AI is the next wave", "prediction"),
            ("Annual cadence of new chips", "strategy"),
            ("No task is beneath me", "principle"),
            ("Accelerated computing is sustainable", "principle"),
            ("Failure drives innovation", "principle"),
            ("AI is the most important technology", "vision"),
        ]
        for i, (name, cat) in enumerate(narratives):
            session.add(Narrative(narrative_name=name, category=cat, significance=0.9 - i*0.03, context=name))
        await session.commit()
        print("已插入 " + str(len(narratives)) + " 个叙事框架")

        # ============ 快照 ============
        total = (await session.execute(select(func.count(Speech.id)))).scalar()
        session.add(Snapshot(name="完整数据快照 2026-06", description="包含黄仁勋生平、全部演讲、财报、叙事（附信源）",
            speech_count=total, analysis_data={"total": total}, summary="共"+str(total)+"条演讲 | 15个叙事框架 | 10期财务数据 | 全部附信源链接"))
        await session.commit()
        print("快照已创建")

        rows = await session.execute(select(Speech.source_type, func.count(Speech.id)).group_by(Speech.source_type).order_by(func.count(Speech.id).desc()))
        print("\n数据汇总:")
        for t, c in rows:
            print("  " + t + ": " + str(c))
        print("共 " + str(total) + " 条，全部附带 source_url")


if __name__ == "__main__":
    asyncio.run(reload())
