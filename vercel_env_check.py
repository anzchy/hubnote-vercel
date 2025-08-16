#!/usr/bin/env python3
"""
Vercel 环境配置检查脚本
用于诊断 Vercel 部署中的配置问题
"""

import os
import json
from utils.storage import StorageManager
from utils.auth import AuthManager

def check_vercel_environment():
    """检查 Vercel 环境配置"""
    print("=== Vercel 环境配置检查 ===")
    print()
    
    # 检查环境变量
    print("环境变量检查:")
    print(f"  - STORAGE_TYPE: {os.getenv('STORAGE_TYPE', '未设置')}")
    print(f"  - KV_REST_API_URL: {os.getenv('KV_REST_API_URL', '未设置')}")
    print(f"  - KV_REST_API_TOKEN: {'已设置' if os.getenv('KV_REST_API_TOKEN') else '未设置'}")
    print(f"  - BLOB_READ_WRITE_TOKEN: {'已设置' if os.getenv('BLOB_READ_WRITE_TOKEN') else '未设置'}")
    print(f"  - GITHUB_TOKEN: {'已设置' if os.getenv('GITHUB_TOKEN') else '未设置'}")
    print(f"  - SECRET_KEY: {'已设置' if os.getenv('SECRET_KEY') else '未设置'}")
    print()
    
    # 检查存储管理器
    print("存储管理器检查:")
    try:
        storage = StorageManager()
        print(f"  - 存储类型: {storage.storage_type}")
        print(f"  - KV URL: {storage.kv_url}")
        print(f"  - KV Token: {'已设置' if storage.kv_token else '未设置'}")
        
        # 测试存储功能
        print("\n存储功能测试:")
        
        # 测试获取仓库
        repos = storage.get_repos()
        print(f"  - 获取仓库: {'成功' if repos else '失败'}")
        print(f"  - 仓库数量: {len(repos.get('repositories', []))}")
        
        # 测试获取白名单
        whitelist = storage.get_user_whitelist()
        print(f"  - 获取白名单: {'成功' if whitelist else '失败'}")
        print(f"  - 白名单用户: {whitelist.get('allowed_users', [])}")
        
        # 测试保存功能
        test_data = {'test': 'data', 'timestamp': '2025-08-16'}
        save_result = storage.save_repos(test_data)
        print(f"  - 保存测试数据: {'成功' if save_result else '失败'}")
        
    except Exception as e:
        print(f"  - 存储管理器初始化失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # 检查认证管理器
    print("认证管理器检查:")
    try:
        auth_manager = AuthManager()
        print(f"  - 认证管理器初始化: 成功")
        
        # 测试白名单功能
        test_username = "test_user"
        add_result = auth_manager.add_user_to_whitelist(test_username, is_admin=False)
        print(f"  - 添加测试用户: {'成功' if add_result else '失败'}")
        
        # 清理测试用户
        if add_result:
            auth_manager.remove_user_from_whitelist(test_username)
            print(f"  - 清理测试用户: 成功")
        
    except Exception as e:
        print(f"  - 认证管理器初始化失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=== 检查完成 ===")

def main():
    """主函数"""
    check_vercel_environment()

if __name__ == '__main__':
    main()
