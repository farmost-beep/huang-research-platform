from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import engine, async_session
from database.models import Base
from api.routes_speeches import router as speeches_router
from api.routes_analysis import router as analysis_router
from api.routes_snapshots import router as snapshots_router
from api.routes_dashboard import router as dashboard_router
from collectors.scheduler import SchedulerService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 启动调度器
    scheduler = SchedulerService()
    await scheduler.start()

    yield

    # 关闭调度器
    await scheduler.stop()
    await engine.dispose()


app = FastAPI(title="黄仁勋深度研究分析平台", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(speeches_router, prefix="/api/speeches", tags=["speeches"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
app.include_router(snapshots_router, prefix="/api/snapshots", tags=["snapshots"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    return {"service": "黄仁勋深度研究分析平台", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
