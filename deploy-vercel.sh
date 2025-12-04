#!/bin/bash
# Vercel 部署脚本
# 使用方法: ./deploy-vercel.sh [--token YOUR_TOKEN] [--prod]

set -e

echo "🚀 开始部署到 Vercel..."

# 切换到项目目录
cd "$(dirname "$0")"

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    echo "⚠️  警告: 有未提交的更改"
    git status -s
    read -p "是否继续部署? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 取消部署"
        exit 1
    fi
fi

# 解析参数
DEPLOY_ARGS=""
PROD_FLAG=""

for arg in "$@"; do
    case $arg in
        --token)
            DEPLOY_ARGS="$DEPLOY_ARGS --token $2"
            shift 2
            ;;
        --prod)
            PROD_FLAG="--prod"
            echo "📦 生产环境部署模式"
            shift
            ;;
        *)
            ;;
    esac
done

# 显示当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 当前分支: $CURRENT_BRANCH"

# 显示最近的提交
echo "📝 最近的提交:"
git log -1 --oneline

# 执行部署
echo ""
echo "🔨 开始部署..."
if [[ -n "$VERCEL_TOKEN" ]]; then
    echo "使用环境变量中的 VERCEL_TOKEN"
    npx vercel --token "$VERCEL_TOKEN" $PROD_FLAG $DEPLOY_ARGS
elif [[ -n "$DEPLOY_ARGS" ]]; then
    npx vercel $DEPLOY_ARGS $PROD_FLAG
else
    echo "⚠️  未提供 Token，将尝试使用已保存的凭据"
    npx vercel $PROD_FLAG
fi

echo ""
echo "✅ 部署完成！"
echo ""
echo "📊 查看部署状态: npx vercel ls"
echo "📋 查看部署日志: npx vercel logs [deployment-url]"
