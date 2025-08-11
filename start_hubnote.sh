#!/bin/bash

# HubNote 应用启动脚本
# 用于 Keyboard Maestro 定时任务

echo "🚀 开始启动 HubNote 应用..."

# 切换到项目目录
cd /Users/jackcheng/Documents/Program_files/HubNote-app

# 检查目录是否存在
if [ ! -d "$(pwd)" ]; then
    echo "❌ 错误：项目目录不存在"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
conda activate hubnote-env

# 检查虚拟环境是否激活成功
if [ $? -ne 0 ]; then
    echo "❌ 错误：虚拟环境激活失败"
    exit 1
fi

# 启动应用
echo "🎯 启动 HubNote 应用..."
python run.py

echo "✅ HubNote 应用启动完成"