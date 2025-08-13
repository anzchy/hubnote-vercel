#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 StorageManager 的存储功能
"""

import os
import sys
from utils.storage import StorageManager

def test_storage():
    """测试存储功能"""
    print("开始测试 StorageManager...")
    
    # 初始化存储管理器
    storage = StorageManager()
    print(f"存储类型: {storage.storage_type}")
    print(f"Blob Token 配置: {'已配置' if storage.blob_token else '未配置'}")
    
    # 测试获取仓库数据
    print("\n测试获取仓库数据...")
    repos_data = storage.get_repos()
    print(f"获取到的仓库数据: {repos_data}")
    
    # 测试保存仓库数据
    print("\n测试保存仓库数据...")
    test_data = {
        'repositories': [
            {
                'name': 'test-repo',
                'full_name': 'test-user/test-repo',
                'description': '测试仓库',
                'added_at': '2025-01-12T19:00:00'
            }
        ]
    }
    
    success = storage.save_repos(test_data)
    print(f"保存结果: {'成功' if success else '失败'}")
    
    # 再次获取数据验证
    if success:
        print("\n验证保存的数据...")
        saved_data = storage.get_repos()
        print(f"验证结果: {saved_data}")
        
        if saved_data.get('repositories'):
            print("✅ 数据持久化测试成功！")
        else:
            print("❌ 数据持久化测试失败！")
    
if __name__ == '__main__':
    test_storage()