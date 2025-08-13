#!/bin/bash

# HubNote Vercel 部署脚本
echo "🚀 开始部署 HubNote 到 Vercel..."

# 检查是否安装了 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI 未安装，请先安装："
    echo "npm i -g vercel"
    exit 1
fi

# 检查是否登录了 Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 请先登录 Vercel："
    vercel login
fi

echo "📋 检查项目配置..."

# 检查必要文件
if [ ! -f "vercel.json" ]; then
    echo "❌ 缺少 vercel.json 配置文件"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ 缺少 requirements.txt 依赖文件"
    exit 1
fi

if [ ! -f "api/index.py" ]; then
    echo "❌ 缺少主入口文件 api/index.py"
    exit 1
fi

echo "✅ 项目配置检查完成"

# 显示当前配置
echo "📊 当前项目信息："
echo "   - 入口文件: api/index.py"
echo "   - 静态文件: static/"
echo "   - 模板文件: templates/"
echo "   - 存储方案: 本地文件 + Vercel KV 降级"

echo ""
echo "⚙️  环境变量设置提醒："
echo "   请确保在 Vercel 项目设置中配置以下环境变量："
echo "   - GITHUB_TOKEN: 您的 GitHub Personal Access Token"
echo "   - SECRET_KEY: Flask 应用密钥"
echo "   - STORAGE_TYPE: vercel_kv (可选，默认使用文件存储)"
echo ""

# 询问是否继续部署
read -p "🤔 是否继续部署？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

echo "📦 开始部署..."

# 部署到 Vercel
if vercel --prod; then
    echo ""
    echo "🎉 部署成功！"
    echo ""
    echo "📋 后续步骤："
    echo "1. 在 Vercel 控制台配置环境变量"
    echo "2. 访问您的应用 URL"
    echo "3. 使用设置向导配置 GitHub Token"
    echo "4. 开始添加仓库和管理 Issues"
    echo ""
    echo "📚 更多信息请查看 VERCEL_DEPLOYMENT.md"
else
    echo ""
    echo "❌ 部署失败，请检查错误信息"
    echo ""
    echo "🔧 常见解决方案："
    echo "1. 检查 vercel.json 配置"
    echo "2. 确认所有依赖都在 requirements.txt 中"
    echo "3. 检查代码中的导入路径"
    echo "4. 查看 Vercel 控制台的构建日志"
    exit 1
fi
