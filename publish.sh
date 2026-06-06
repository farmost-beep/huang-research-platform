#!/bin/bash
# =============================================================
# GitHub 发布脚本 — 在你的 Mac 终端运行
# =============================================================
set -e

echo "=========================================="
echo "  发布到 GitHub"
echo "=========================================="

cd /Users/cyingfang/web

# 1. 初始化 git（如果还没有）
if [ ! -d .git ]; then
  git init
  git add -A
  git commit -m "🎬 黄仁勋深度研究分析平台 - 初始版本

全栈架构：FastAPI + React + PostgreSQL/pgvector + Claude API
功能：演讲采集 / 主题分析 / 情感趋势 / 叙事框架 / 快照系统
分析维度：主题演化 / 叙事框架 / 领导力画像 / 预测回溯"
fi

# 2. GitHub 登录
gh auth login -h github.com -w

# 3. 创建仓库并推送
gh repo create huang-research-platform --public --source=. --remote=origin --push

echo ""
echo "✅ 已发布到: https://github.com/farmost-beep/huang-research-platform"
echo ""
echo "启动方式："
echo "  cd /Users/cyingfang/web"
echo "  bash setup.sh"
echo ""
