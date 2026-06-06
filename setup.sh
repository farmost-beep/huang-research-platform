#!/bin/bash
# =============================================================
# 黄仁勋深度研究分析平台 - 一键安装脚本
# 在你的 Mac 终端直接运行: bash setup.sh
# =============================================================
set -e

echo "=========================================="
echo "  黄仁勋深度研究分析平台 - 环境安装"
echo "=========================================="

# 1. 修复 Homebrew 权限
echo ""
echo "[1/6] 修复 Homebrew 权限..."
sudo chown -R $(whoami) /opt/homebrew /Users/$(whoami)/Library/Caches/Homebrew /Users/$(whoami)/Library/Logs/Homebrew 2>/dev/null || true

# 2. 安装 PostgreSQL + pgvector
echo ""
echo "[2/6] 安装 PostgreSQL + pgvector..."
brew install postgresql pgvector 2>/dev/null || echo "  → 可能已安装"

# 3. 启动 PostgreSQL
echo ""
echo "[3/6] 启动 PostgreSQL..."
brew services restart postgresql 2>/dev/null || pg_ctl -D /opt/homebrew/var/postgresql@16 start 2>/dev/null || echo "  → 请手动启动: brew services start postgresql"
sleep 2

# 4. 创建数据库用户和库
echo ""
echo "[4/6] 创建数据库..."
createuser -s huang 2>/dev/null || echo "  → 用户已存在"
psql -U huang -c "ALTER USER huang PASSWORD 'huang_secret';" 2>/dev/null || echo "  → 密码设置略过"
createdb -U huang huang_research 2>/dev/null || echo "  → 数据库已存在"
psql -U huang -d huang_research -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || true

# 5. 安装 Python 依赖
echo ""
echo "[5/6] 安装 Python 依赖..."
cd "$(dirname "$0")/backend"
pip3 install -r requirements.txt 2>/dev/null || pip3 install --proxy '' -r requirements.txt

# 6. 安装前端依赖
echo ""
echo "[6/6] 安装前端依赖..."
cd "$(dirname "$0")/frontend"
npm install 2>/dev/null || npm install --no-proxy

echo ""
echo "=========================================="
echo "  安装完成！启动方式："
echo "=========================================="
echo ""
echo "  终端 1 - 启动后端:"
echo "    cd $(dirname "$0")/backend"
echo "    uvicorn main:app --reload --port 8000"
echo ""
echo "  终端 2 - 启动前端:"
echo "    cd $(dirname "$0")/frontend"
echo "    npm run dev"
echo ""
echo "  访问: http://localhost:3000"
echo ""
echo "  如需配置 API Key:"
echo "    编辑 backend/.env 填入 CLAUDE_API_KEY"
echo "=========================================="
