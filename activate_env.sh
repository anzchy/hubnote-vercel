#!/bin/bash
# GitNote 虚拟环境激活脚本

echo "🚀 激活 GitNote 虚拟环境..."
source gitnote-venv/bin/activate

echo "✅ 虚拟环境已激活"
echo "📍 Python 路径: $(which python)"
echo "📦 Pip 路径: $(which pip)"
echo ""
echo "现在你可以运行以下命令启动应用:"
echo "  python run.py"
echo ""
echo "要退出虚拟环境，请输入: deactivate"
echo ""