#!/usr/bin/env python3
"""
Vercel KV 诊断脚本
用于检查 KV 中的数据和用户权限
"""

import os
import sys
from utils.storage import StorageManager

def main():
    print("=" * 60)
    print("🔍 Vercel KV 诊断工具")
    print("=" * 60)
    print()
    
    # 检查环境变量
    print("📋 环境变量检查:")
    print(f"  - STORAGE_TYPE: {os.getenv('STORAGE_TYPE', '未设置')}")
    print(f"  - KV_REST_API_URL: {'已设置' if os.getenv('KV_REST_API_URL') else '未设置'}")
    print(f"  - KV_REST_API_TOKEN: {'已设置' if os.getenv('KV_REST_API_TOKEN') else '未设置'}")
    print(f"  - DEFAULT_ADMIN_USER: {os.getenv('DEFAULT_ADMIN_USER', '未设置')}")
    print(f"  - VERCEL: {os.getenv('VERCEL', '未设置')}")
    print(f"  - VERCEL_ENV: {os.getenv('VERCEL_ENV', '未设置')}")
    print()
    
    # 初始化存储
    print("🔧 初始化 StorageManager...")
    storage = StorageManager()
    print(f"  - 存储类型: {storage.storage_type}")
    print(f"  - 是否 Vercel 环境: {storage.is_vercel}")
    print()
    
    # 检查用户白名单
    print("👥 用户白名单:")
    whitelist = storage.get_user_whitelist()
    print(f"  - 允许的用户: {whitelist.get('allowed_users', [])}")
    print(f"  - 管理员用户: {whitelist.get('admin_users', [])}")
    print()
    
    # 检查仓库数据
    print("📦 仓库数据:")
    repos_data = storage.get_repos()
    repos = repos_data.get('repositories', [])
    print(f"  - 仓库总数: {len(repos)}")
    if repos:
        print("  - 仓库列表:")
        for repo in repos:
            print(f"    • {repo.get('full_name')} (添加人: {repo.get('added_by', '未知')})")
    else:
        print("  - ⚠️ 没有仓库数据")
    print()
    
    # 模拟用户权限检查
    test_user = os.getenv('DEFAULT_ADMIN_USER', 'anzchy')
    print(f"🧪 测试用户 '{test_user}' 的权限:")
    is_admin = test_user in whitelist.get('admin_users', [])
    print(f"  - 是否管理员: {is_admin}")
    
    user_repos = storage.get_user_repos(test_user, is_admin)
    user_repo_list = user_repos.get('repositories', [])
    print(f"  - 可见仓库数: {len(user_repo_list)}")
    
    if user_repo_list:
        print("  - 可见仓库:")
        for repo in user_repo_list:
            print(f"    • {repo.get('full_name')}")
    else:
        print("  - ⚠️ 该用户看不到任何仓库")
        print()
        print("🔧 可能的原因:")
        if not is_admin:
            print("  1. 用户不是管理员，只能看到自己添加的仓库")
            print("  2. 没有添加 added_by 字段匹配的仓库")
        if not whitelist.get('admin_users'):
            print("  3. 白名单中没有管理员配置")
        if not repos:
            print("  4. KV 中确实没有仓库数据")
    
    print()
    print("=" * 60)
    print("✅ 诊断完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
