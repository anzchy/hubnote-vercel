#!/bin/bash

# HubNote 应用打包脚本
# 使用 PyInstaller 将 Flask 应用打包为 macOS 应用程序

echo "🚀 开始打包 HubNote 应用..."

# 检查是否安装了 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller 未安装，正在安装..."
    pip install pyinstaller
fi

# 激活虚拟环境（如果存在）
if [ -d "gitnote-venv" ]; then
    echo "📦 激活虚拟环境..."
    source gitnote-venv/bin/activate
fi

# 清理之前的构建文件
echo "🧹 清理之前的构建文件..."
rm -rf build/
rm -rf dist/

# 使用 PyInstaller 打包
echo "📦 开始打包应用..."
pyinstaller HubNote.spec

# 检查打包是否成功
if [ -d "dist/HubNote.app" ]; then
    echo "✅ 打包成功！"
    echo "📱 应用位置: $(pwd)/dist/HubNote.app"
    echo ""
    echo "🎉 HubNote.app 已创建完成！"
    echo "💡 您可以将应用拖拽到 Applications 文件夹中使用"
    echo "💡 或者直接双击运行: open dist/HubNote.app"
    
    # 询问是否立即运行
    read -p "🤔 是否立即运行应用？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 启动 HubNote..."
        open dist/HubNote.app
    fi
else
    echo "❌ 打包失败，请检查错误信息"
    exit 1
fi

echo "✨ 打包完成！"