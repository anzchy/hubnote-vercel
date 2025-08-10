#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Token 测试脚本
用于验证 GitHub Token 的有效性和权限
"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_github_token():
    """测试 GitHub Token 的有效性"""
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ 错误: 未找到 GITHUB_TOKEN 环境变量")
        return False
    
    print(f"🔑 测试 GitHub Token: {token[:10]}...{token[-4:]}")
    print("="*50)
    
    # 测试 1: 验证 Token 基本信息
    print("📋 测试 1: 验证 Token 基本信息")
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token 有效")
            print(f"   用户: {user_info.get('login')}")
            print(f"   用户名: {user_info.get('name', 'N/A')}")
            print(f"   邮箱: {user_info.get('email', 'N/A')}")
        elif response.status_code == 401:
            print(f"❌ Token 无效或已过期")
            print(f"   响应: {response.json()}")
            return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False
    
    # 测试 2: 检查 API 限制
    print("\n📊 测试 2: 检查 API 限制")
    try:
        response = requests.get('https://api.github.com/rate_limit', headers=headers)
        if response.status_code == 200:
            rate_limit = response.json()
            core = rate_limit['resources']['core']
            print(f"✅ API 限制信息:")
            print(f"   剩余请求: {core['remaining']}/{core['limit']}")
            print(f"   重置时间: {core['reset']}")
        else:
            print(f"❌ 获取 API 限制失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取 API 限制异常: {e}")
    
    # 测试 3: 测试仓库访问
    print("\n🏗️ 测试 3: 测试公共仓库访问")
    test_repos = [
        'octocat/Hello-World',
        'microsoft/vscode',
        'facebook/react'
    ]
    
    for repo in test_repos:
        try:
            response = requests.get(f'https://api.github.com/repos/{repo}', headers=headers)
            if response.status_code == 200:
                repo_info = response.json()
                print(f"✅ {repo}: 可访问 (⭐ {repo_info['stargazers_count']})")
                break
            elif response.status_code == 404:
                print(f"❌ {repo}: 404 Not Found")
            else:
                print(f"❌ {repo}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"❌ {repo}: 异常 - {e}")
    
    # 测试 4: 检查 Token 权限范围
    print("\n🔐 测试 4: 检查 Token 权限范围")
    try:
        # 从响应头中获取权限范围
        response = requests.get('https://api.github.com/user', headers=headers)
        if 'X-OAuth-Scopes' in response.headers:
            scopes = response.headers['X-OAuth-Scopes']
            print(f"✅ Token 权限范围: {scopes}")
            
            # 检查必要权限
            required_scopes = ['repo', 'public_repo']
            has_required = any(scope.strip() in scopes for scope in required_scopes)
            
            if has_required:
                print("✅ 具备访问仓库的必要权限")
            else:
                print("⚠️ 可能缺少访问仓库的权限")
                print("   建议权限: repo 或 public_repo")
        else:
            print("❌ 无法获取权限范围信息")
    except Exception as e:
        print(f"❌ 检查权限异常: {e}")
    
    print("\n" + "="*50)
    print("🎯 测试完成")
    return True

def get_token_help():
    """显示获取 GitHub Token 的帮助信息"""
    print("\n📖 如何获取 GitHub Personal Access Token:")
    print("1. 访问 https://github.com/settings/tokens")
    print("2. 点击 'Generate new token' -> 'Generate new token (classic)'")
    print("3. 设置 Token 名称和过期时间")
    print("4. 选择权限范围:")
    print("   - repo: 访问私有仓库")
    print("   - public_repo: 访问公共仓库")
    print("   - read:org: 读取组织信息")
    print("5. 点击 'Generate token'")
    print("6. 复制生成的 Token 并保存到 .env 文件中")
    print("\n⚠️ 注意: Token 只显示一次，请妥善保存!")

if __name__ == '__main__':
    print("🚀 GitHub Token 测试工具")
    print("="*50)
    
    success = test_github_token()
    
    if not success:
        get_token_help()
        print("\n💡 解决方案:")
        print("1. 检查 .env 文件中的 GITHUB_TOKEN 是否正确")
        print("2. 确认 Token 未过期")
        print("3. 验证 Token 具有必要的权限")
        print("4. 如果问题持续，请生成新的 Token")