#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库访问测试脚本
用于测试特定 GitHub 仓库的访问性
"""

import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.github_service import GitHubService

# 加载环境变量
load_dotenv()

def test_repo_access(repo_url):
    """测试仓库访问"""
    print(f"🔍 测试仓库访问: {repo_url}")
    print("="*60)
    
    # 检查 GitHub Token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ 错误: 未找到 GITHUB_TOKEN 环境变量")
        return False
    
    # 创建 GitHub 服务实例
    try:
        github_service = GitHubService()
        print(f"✅ GitHub 服务初始化成功")
    except Exception as e:
        print(f"❌ GitHub 服务初始化失败: {e}")
        return False
    
    # 测试仓库访问
    print(f"\n📋 正在获取仓库信息...")
    result = github_service.get_repo_info(repo_url)
    
    if result['success']:
        repo_data = result['data']
        print(f"✅ 仓库访问成功!")
        print(f"\n📊 仓库信息:")
        print(f"   完整名称: {repo_data['full_name']}")
        print(f"   仓库名: {repo_data['name']}")
        print(f"   所有者: {repo_data['owner']}")
        print(f"   描述: {repo_data['description'] or 'N/A'}")
        print(f"   语言: {repo_data['language'] or 'N/A'}")
        print(f"   星标数: {repo_data['stars']}")
        print(f"   Fork 数: {repo_data['forks']}")
        print(f"   开放 Issues: {repo_data['open_issues']}")
        print(f"   创建时间: {repo_data['created_at']}")
        print(f"   更新时间: {repo_data['updated_at']}")
        print(f"   GitHub 链接: {repo_data['url']}")
        
        # 测试 Issues 访问
        print(f"\n🐛 测试 Issues 访问...")
        issues_result = github_service.get_issues(repo_data['full_name'], page=1, per_page=5)
        
        if issues_result['success']:
            issues = issues_result['data']
            print(f"✅ Issues 访问成功! 找到 {len(issues)} 个 Issues")
            
            if issues:
                print(f"\n📝 最近的 Issues:")
                for i, issue in enumerate(issues[:3], 1):
                    print(f"   {i}. #{issue['number']}: {issue['title'][:50]}{'...' if len(issue['title']) > 50 else ''}")
                    print(f"      状态: {issue['state']} | 评论: {issue['comments_count']} | 作者: {issue['user']['login']}")
            else:
                print(f"   该仓库暂无 Issues")
        else:
            print(f"❌ Issues 访问失败: {issues_result['error']}")
        
        return True
    else:
        print(f"❌ 仓库访问失败!")
        print(f"\n🔍 错误详情:")
        print(f"   {result['error']}")
        
        # 提供解决建议
        print(f"\n💡 解决建议:")
        if '404' in result['error']:
            print(f"   1. 检查仓库名是否正确拼写")
            print(f"   2. 确认仓库是否存在（可能已被删除或重命名）")
            print(f"   3. 如果是私有仓库，确保 Token 有访问权限")
            print(f"   4. 尝试在浏览器中访问: https://github.com/{repo_url}")
        elif '403' in result['error']:
            print(f"   1. 检查 API 请求限制是否已达上限")
            print(f"   2. 确认 Token 权限是否足够")
            print(f"   3. 如果是私有仓库，确保有访问权限")
        elif '401' in result['error']:
            print(f"   1. 检查 .env 文件中的 GITHUB_TOKEN 是否正确")
            print(f"   2. 确认 Token 是否已过期")
            print(f"   3. 重新生成 GitHub Personal Access Token")
        
        return False

def main():
    """主函数"""
    print("🚀 GitHub 仓库访问测试工具")
    print("="*60)
    
    # 获取命令行参数
    if len(sys.argv) > 1:
        repo_url = sys.argv[1]
    else:
        # 交互式输入
        print("请输入要测试的仓库 URL 或 owner/repo 格式:")
        print("示例:")
        print("  - https://github.com/microsoft/vscode")
        print("  - microsoft/vscode")
        print("  - octocat/Hello-World")
        print()
        repo_url = input("仓库 URL: ").strip()
    
    if not repo_url:
        print("❌ 错误: 请提供仓库 URL")
        sys.exit(1)
    
    # 测试仓库访问
    success = test_repo_access(repo_url)
    
    print("\n" + "="*60)
    if success:
        print("🎉 测试完成: 仓库访问正常")
        print("\n现在您可以在 GitNote 应用中添加这个仓库了!")
    else:
        print("❌ 测试失败: 仓库访问异常")
        print("\n请根据上述建议解决问题后重试")
    
    return success

if __name__ == '__main__':
    main()