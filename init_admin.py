#!/usr/bin/env python3
"""
初始化管理员用户脚本
用于设置第一个管理员用户，避免无法访问用户管理功能的问题
"""

import os
import sys

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from utils.storage import StorageManager
from utils.auth import AuthManager

def init_admin_user():
    """初始化管理员用户"""
    print("=== HubNote 管理员初始化工具 ===")
    print()
    
    # 获取用户输入
    username = input("请输入要设置为管理员的 GitHub 用户名: ").strip()
    
    if not username:
        print("错误: 用户名不能为空")
        return False
    
    # 确认操作
    confirm = input(f"确定要将 '{username}' 设置为管理员吗? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("操作已取消")
        return False
    
    try:
        # 初始化管理器
        auth_manager = AuthManager()
        
        # 添加管理员用户
        success = auth_manager.add_user_to_whitelist(username, is_admin=True)
        
        if success:
            print(f"✅ 成功将 '{username}' 设置为管理员")
            print()
            print("现在您可以:")
            print(f"1. 使用 GitHub 用户名 '{username}' 和对应的 Personal Access Token 登录")
            print("2. 登录后访问 '用户管理' 页面管理其他用户")
            print("3. 添加更多用户到白名单")
            print()
            print("注意: Personal Access Token 需要有 repo 权限")
            return True
        else:
            print("❌ 设置管理员失败")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def show_current_whitelist():
    """显示当前白名单"""
    try:
        storage = StorageManager()
        whitelist = storage.get_user_whitelist()
        
        print("=== 当前用户白名单 ===")
        print()
        
        allowed_users = whitelist.get('allowed_users', [])
        admin_users = whitelist.get('admin_users', [])
        
        if not allowed_users:
            print("白名单为空 (所有用户都可以访问)")
        else:
            print("允许访问的用户:")
            for user in allowed_users:
                role = "管理员" if user in admin_users else "普通用户"
                print(f"  - {user} ({role})")
        
        print()
        
    except Exception as e:
        print(f"获取白名单失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        show_current_whitelist()
        return
    
    print("使用说明:")
    print("- 此工具用于初始化第一个管理员用户")
    print("- 管理员可以通过 Web 界面管理其他用户")
    print("- 如果白名单为空，所有用户都可以访问")
    print("- 添加第一个用户后，只有白名单中的用户才能访问")
    print()
    
    # 显示当前状态
    show_current_whitelist()
    
    # 初始化管理员
    success = init_admin_user()
    
    if success:
        print()
        show_current_whitelist()

if __name__ == '__main__':
    main()