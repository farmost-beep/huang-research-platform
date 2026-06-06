# 黄仁勋深度研究分析平台

系统采集黄仁勋所有公开发言，结合 NVIDIA 公司经营情况，进行多维度深度分析。

## 快速启动（Mac 本地）

### 1. 安装依赖

```bash
# 后端
cd /Users/cyingfang/web/backend
pip3 install -r requirements.txt

# 前端
cd /Users/cyingfang/web/frontend
npm install
```

### 2. 启动数据库

```bash
# 需要先安装 Docker Desktop for Mac
# 只需要启动 PostgreSQL
cd /Users/cyingfang/web
docker compose up db -d
```

### 3. 配置环境变量（可选）

```bash
cd /Users/cyingfang/web/backend
echo "CLAUDE_API_KEY=sk-ant-xxxxxxxx" > .env
echo "YOUTUBE_API_KEY=xxxxxxxx" >> .env
```

无 API Key 时自动使用规则分析引擎（不含 Claude 深度语义分析）。

### 4. 启动后端

```bash
cd /Users/cyingfang/web/backend
python3 seed_data.py    # 首次：创建表 + 采集种子数据 + 初始分析
uvicorn main:app --reload --port 8000
```

### 5. 启动前端（新终端）

```bash
cd /Users/cyingfang/web/frontend
npm run dev
```

访问 http://localhost:3000

### 6. 一键启动（Docker）

```bash
cd /Users/cyingfang/web
docker compose up
```

## 系统架构

```
Dashboard (/)
  ├── 统计卡片     — 演讲数/总字数/时间跨度/来源数
  ├── 来源分布     — keynote/earnings/interview/conference
  ├── 高频词云     — ECharts 词云图
  └── 最近演讲     — 最新 5 篇 + 快照状态

时间线 (/timeline)
  ├── 按年份分组   — 年度聚合
  ├── 类型筛选     — keynote/earnings/interview/conference
  └── 可点击进入详情

主题分析 (/topics)
  ├── 主题排名     — Top 20 主题 + 相关度条
  ├── 主题演化     — 河流图（主题随时间强度变化）
  ├── 词云         — ECharts 词云
  ├── 情感趋势     — 月度情感折线图
  └── 叙事框架     — 比喻/预测/原则/战略分类

快照 (/snapshots)
  ├── 快照列表     — 所有快照卡片
  └── 生成快照     — 手动触发

演讲详情 (/speech/:id)
  ├── 原文         — 演讲正文
  └── 分析侧栏     — 主题/情感/叙事分析结果
```
