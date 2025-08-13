import os
import jwt
import time
from typing import Dict, Any, Optional
from services.github_service import GitHubService
from utils.storage import StorageManager

class AuthManager:
    """认证管理器，处理用户认证和权限验证"""
    
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', 'vercel-secret-key')
        self.token_expiry = 24 * 60 * 60  # 24小时
        self.storage = StorageManager()
    
    def create_user_token(self, user_data: Dict[str, Any]) -> str:
        """创建用户认证令牌"""
        payload = {
            'user_id': user_data.get('login'),
            'username': user_data.get('login'),
            'avatar_url': user_data.get('avatar_url'),
            'exp': time.time() + self.token_expiry,
            'iat': time.time()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_user_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证用户认证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # 检查令牌是否过期
            if payload.get('exp', 0) < time.time():
                return None
            
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'avatar_url': payload.get('avatar_url')
            }
        except jwt.InvalidTokenError:
            return None
    
    def get_user_from_request(self, request) -> Optional[Dict[str, Any]]:
        """从请求中获取用户信息"""
        # 从 Authorization 头获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]  # 移除 'Bearer ' 前缀
            return self.verify_user_token(token)
        
        # 从 Cookie 获取令牌
        token = request.cookies.get('auth_token')
        if token:
            return self.verify_user_token(token)
        
        return None
    
    def is_user_allowed(self, username: str) -> bool:
        """检查用户是否在白名单中"""
        try:
            whitelist = self.storage.get_user_whitelist()
            allowed_users = whitelist.get('allowed_users', [])
            
            # 如果白名单为空，允许所有用户（向后兼容）
            if not allowed_users:
                return True
            
            return username.lower() in [user.lower() for user in allowed_users]
        except Exception as e:
            print(f"检查用户白名单失败: {e}")
            # 出错时默认允许（安全考虑）
            return True
    
    def is_user_admin(self, username: str) -> bool:
        """检查用户是否为管理员"""
        try:
            whitelist = self.storage.get_user_whitelist()
            admin_users = whitelist.get('admin_users', [])
            return username.lower() in [user.lower() for user in admin_users]
        except Exception as e:
            print(f"检查管理员权限失败: {e}")
            return False
    
    def add_user_to_whitelist(self, username: str, is_admin: bool = False) -> bool:
        """添加用户到白名单"""
        try:
            whitelist = self.storage.get_user_whitelist()
            allowed_users = whitelist.get('allowed_users', [])
            admin_users = whitelist.get('admin_users', [])
            
            username_lower = username.lower()
            
            # 添加到允许用户列表
            if username_lower not in [user.lower() for user in allowed_users]:
                allowed_users.append(username)
            
            # 如果是管理员，添加到管理员列表
            if is_admin and username_lower not in [user.lower() for user in admin_users]:
                admin_users.append(username)
            
            whitelist['allowed_users'] = allowed_users
            whitelist['admin_users'] = admin_users
            
            return self.storage.save_user_whitelist(whitelist)
        except Exception as e:
            print(f"添加用户到白名单失败: {e}")
            return False
    
    def remove_user_from_whitelist(self, username: str) -> bool:
        """从白名单中移除用户"""
        try:
            whitelist = self.storage.get_user_whitelist()
            allowed_users = whitelist.get('allowed_users', [])
            admin_users = whitelist.get('admin_users', [])
            
            username_lower = username.lower()
            
            # 从允许用户列表中移除
            allowed_users = [user for user in allowed_users if user.lower() != username_lower]
            # 从管理员列表中移除
            admin_users = [user for user in admin_users if user.lower() != username_lower]
            
            whitelist['allowed_users'] = allowed_users
            whitelist['admin_users'] = admin_users
            
            return self.storage.save_user_whitelist(whitelist)
        except Exception as e:
            print(f"从白名单移除用户失败: {e}")
            return False
    
    def check_repo_permission(self, github_service: GitHubService, 
                             repo_full_name: str, 
                             user_id: str, 
                             required_permission: str = 'push') -> bool:
        """检查用户对仓库的权限"""
        try:
            # 获取仓库信息
            repo = github_service.github.get_repo(repo_full_name)
            
            # 检查用户权限
            if required_permission == 'admin':
                return repo.permissions.admin
            elif required_permission == 'push':
                return repo.permissions.push
            elif required_permission == 'pull':
                return repo.permissions.pull
            else:
                return False
        except Exception as e:
            print(f"检查仓库权限失败: {e}")
            return False
    
    def require_auth(self, f):
        """认证装饰器"""
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            user = self.get_user_from_request(request)
            if not user:
                return jsonify({
                    'success': False,
                    'error': '需要认证'
                }), 401
            
            # 将用户信息添加到请求上下文
            request.user = user
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    def require_repo_permission(self, permission: str = 'push'):
        """仓库权限装饰器"""
        def decorator(f):
            def decorated_function(*args, **kwargs):
                from flask import request, jsonify
                
                user = self.get_user_from_request(request)
                if not user:
                    return jsonify({
                        'success': False,
                        'error': '需要认证'
                    }), 401
                
                # 获取仓库名称
                repo_full_name = kwargs.get('repo_full_name')
                if not repo_full_name:
                    return jsonify({
                        'success': False,
                        'error': '缺少仓库信息'
                    }), 400
                
                # 检查权限
                github_service = GitHubService(os.getenv('GITHUB_TOKEN'))
                if not self.check_repo_permission(github_service, repo_full_name, 
                                                user['user_id'], permission):
                    return jsonify({
                        'success': False,
                        'error': f'权限不足，需要 {permission} 权限'
                    }), 403
                
                request.user = user
                return f(*args, **kwargs)
            
            decorated_function.__name__ = f.__name__
            return decorated_function
        return decorator
