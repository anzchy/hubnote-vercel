#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitNote 应用启动脚本

使用方法:
    python run.py
    或
    python run.py --host 0.0.0.0 --port 8000
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='HubNote - GitHub Issues 管理工具')
    
    # 检测是否为打包后的应用
    is_packaged = getattr(sys, '_MEIPASS', None) is not None
    default_port = 5001 if is_packaged else 5000
    
    parser.add_argument('--host', default='127.0.0.1', help='监听地址')
    parser.add_argument('--port', type=int, default=default_port, help='监听端口')
    parser.add_argument('--debug', action='store_true', default=False, help='调试模式')
    
    args = parser.parse_args()
    
    # 创建必要的目录
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 检查数据文件
    repos_file = Config.REPOS_FILE
    if not os.path.exists(repos_file):
        print(f"📁 创建数据文件: {repos_file}")
        with open(repos_file, 'w', encoding='utf-8') as f:
            import json
            json.dump({"repositories": []}, f, indent=2)
    
    print("🚀 启动 HubNote 应用...")
    print(f"📍 地址: http://{args.host}:{args.port}")
    print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
    print("\n按 Ctrl+C 停止应用\n")
    
    # 创建应用实例
    app = create_app()
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or Config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()