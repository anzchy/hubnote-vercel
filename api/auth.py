from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template, session, make_response
from services.github_service import GitHubService
from utils.storage import StorageManager
from utils.auth import AuthManager
import os

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

# 初始化服务
auth_manager = AuthManager()
storage = StorageManager()

def get_github_service():
    """获取当前用户的 GitHub 服务实例"""
    github_token = session.get('github_token')
    if not github_token:
        return None
    return GitHubService(github_token)

@auth_bp.route('/api/validate_token', methods=['GET'])
def api_validate_token():
    """验证 GitHub Token"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'message': '未登录或 Token 无效'
        }), 401
    
    success, message = github_service.validate_token()
    return jsonify({
        'success': success,
        'message': message
    })

@auth_bp.route('/api/config', methods=['GET'])
def api_get_config():
    """获取配置信息"""
    user_config = storage.get_user_preferences('default')
    github_service = get_github_service()
    token_valid = bool(github_service and github_service.validate_token()[0]) if github_service else False
    
    return jsonify({
        'has_token': bool(session.get('github_token')),
        'token_valid': token_valid,
        'storage_type': os.getenv('STORAGE_TYPE', 'vercel_kv'),
        'user_preferences': user_config
    })

@auth_bp.route('/api/user', methods=['GET'])
def api_get_current_user():
    """获取当前用户信息"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '未登录或 Token 无效'
        }), 401
    
    result = github_service.get_current_user()
    return jsonify(result)

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """用户登录（验证 GitHub Token 并创建会话）"""
    data = request.get_json()
    token = data.get('token', '').strip()
    
    if not token:
        return jsonify({
            'success': False,
            'error': 'Token 不能为空'
        }), 400
    
    try:
        # 验证 token
        temp_service = GitHubService(token)
        success, message = temp_service.validate_token()
        
        if not success:
            return jsonify({
                'success': False,
                'error': f'Token 验证失败: {message}'
            }), 400
        
        # 获取用户信息
        user_result = temp_service.get_current_user()
        if not user_result['success']:
            return jsonify({
                'success': False,
                'error': '获取用户信息失败'
            }), 500
        
        # 创建用户令牌
        user_data = user_result['data']
        user_token = auth_manager.create_user_token(user_data)
        
        # 保存用户偏好设置
        user_prefs = storage.get_user_preferences(user_data['login'])
        user_prefs['last_login'] = user_data.get('login')
        user_prefs['github_token'] = token  # 注意：实际生产环境不应存储原始 token
        storage.save_user_preferences(user_data['login'], user_prefs)
        
        # 创建响应
        response = make_response(jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'user': user_data,
                'token': user_token
            }
        }))
        
        # 设置 Cookie
        response.set_cookie(
            'user_token', 
            user_token, 
            max_age=24*60*60,  # 24小时
            httponly=True,
            secure=os.getenv('FLASK_ENV') == 'production',
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Web 登录路由
@auth_bp.route('/login', methods=['GET'])
def login_page():
    """显示登录页面"""
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """处理登录请求"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not username or not password:
        return render_template('login.html', error='请输入用户名和密码')
    
    # 使用密码作为 GitHub Token 进行验证
    temp_github_service = GitHubService(password)
    success, message = temp_github_service.validate_token()
    
    if success:
        # 验证成功，获取用户信息
        user_result = temp_github_service.get_current_user()
        if user_result['success'] and user_result['data']['login'] == username:
            # 检查用户是否在白名单中
            if not auth_manager.is_user_allowed(username):
                return render_template('login.html', error='您没有访问权限，请联系管理员')
            
            # 用户名匹配且在白名单中，创建会话
            session['github_token'] = password
            session['username'] = username
            session['user_data'] = user_result['data']
            session['is_admin'] = auth_manager.is_user_admin(username)
            
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名与 GitHub Token 不匹配')
    else:
        return render_template('login.html', error=f'GitHub Token 验证失败: {message}')

@auth_bp.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash('已成功登出', 'success')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """用户登出"""
    response = make_response(jsonify({
        'success': True,
        'message': '登出成功'
    }))
    
    # 清除 Cookie
    response.delete_cookie('user_token')
    
    return response

@auth_bp.route('/api/auth/me', methods=['GET'])
@auth_manager.require_auth
def api_get_me():
    """获取当前登录用户信息"""
    user = request.user
    return jsonify({
        'success': True,
        'data': user
    })

@auth_bp.route('/api/auth/refresh', methods=['POST'])
@auth_manager.require_auth
def api_refresh_token():
    """刷新用户令牌"""
    user = request.user
    
    # 获取 GitHub 服务实例
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '未登录或 Token 无效'
        }), 401
    
    # 获取最新的用户信息
    try:
        user_result = github_service.get_current_user()
        if not user_result['success']:
            return jsonify({
                'success': False,
                'error': '获取用户信息失败'
            }), 500
        
        user_data = user_result['data']
        new_token = auth_manager.create_user_token(user_data)
        
        # 创建响应
        response = make_response(jsonify({
            'success': True,
            'message': '令牌刷新成功',
            'data': {
                'user': user_data,
                'token': new_token
            }
        }))
        
        # 更新 Cookie
        response.set_cookie(
            'user_token', 
            new_token, 
            max_age=24*60*60,
            httponly=True,
            secure=os.getenv('FLASK_ENV') == 'production',
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'令牌刷新失败: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/permissions/<path:repo_full_name>', methods=['GET'])
@auth_manager.require_auth
def api_check_permissions(repo_full_name):
    """检查用户对特定仓库的权限"""
    user = request.user
    
    try:
        # 检查各种权限级别
        permissions = {}
        
        # 检查 pull 权限
        permissions['pull'] = auth_manager.check_repo_permission(
            github_service, repo_full_name, user['user_id'], 'pull'
        )
        
        # 检查 push 权限
        permissions['push'] = auth_manager.check_repo_permission(
            github_service, repo_full_name, user['user_id'], 'push'
        )
        
        # 检查 admin 权限
        permissions['admin'] = auth_manager.check_repo_permission(
            github_service, repo_full_name, user['user_id'], 'admin'
        )
        
        return jsonify({
            'success': True,
            'data': {
                'repo': repo_full_name,
                'user': user['user_id'],
                'permissions': permissions
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'检查权限失败: {str(e)}'
        }), 500

@auth_bp.route('/api/auth/preferences', methods=['GET'])
@auth_manager.require_auth
def api_get_preferences():
    """获取用户偏好设置"""
    user = request.user
    prefs = storage.get_user_preferences(user['user_id'])
    
    return jsonify({
        'success': True,
        'data': prefs
    })

@auth_bp.route('/api/auth/preferences', methods=['PUT'])
@auth_manager.require_auth
def api_update_preferences():
    """更新用户偏好设置"""
    user = request.user
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    try:
        # 获取现有偏好设置
        prefs = storage.get_user_preferences(user['user_id'])
        
        # 更新偏好设置
        prefs.update(data)
        
        # 保存偏好设置
        if storage.save_user_preferences(user['user_id'], prefs):
            return jsonify({
                'success': True,
                'message': '偏好设置更新成功',
                'data': prefs
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存偏好设置失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新偏好设置失败: {str(e)}'
        }), 500

@auth_bp.route('/user-management')
def user_management():
    """用户管理页面"""
    # 检查是否登录
    if 'username' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('auth.login_page'))
    
    # 检查是否为管理员
    if not session.get('is_admin', False):
        flash('您没有管理员权限', 'error')
        return redirect(url_for('index'))
    
    # 获取用户白名单
    whitelist = storage.get_user_whitelist()
    
    return render_template('user_management.html', whitelist=whitelist)

@auth_bp.route('/add-user', methods=['POST'])
def add_user_to_whitelist():
    """添加用户到白名单"""
    # 检查是否登录且为管理员
    if 'username' not in session or not session.get('is_admin', False):
        flash('您没有管理员权限', 'error')
        return redirect(url_for('auth.login_page'))
    
    username = request.form.get('username', '').strip()
    is_admin = 'is_admin' in request.form
    
    if not username:
        flash('请输入用户名', 'error')
        return redirect(url_for('auth.user_management'))
    
    # 添加用户到白名单
    success = auth_manager.add_user_to_whitelist(username, is_admin)
    
    if success:
        role = '管理员' if is_admin else '普通用户'
        flash(f'成功添加用户 {username} ({role})', 'success')
    else:
        flash('添加用户失败', 'error')
    
    return redirect(url_for('auth.user_management'))

@auth_bp.route('/remove-user', methods=['POST'])
def remove_user_from_whitelist():
    """从白名单中移除用户"""
    # 检查是否登录且为管理员
    if 'username' not in session or not session.get('is_admin', False):
        flash('您没有管理员权限', 'error')
        return redirect(url_for('auth.login_page'))
    
    username = request.form.get('username', '').strip()
    current_user = session.get('username')
    
    if not username:
        flash('用户名不能为空', 'error')
        return redirect(url_for('auth.user_management'))
    
    # 防止管理员删除自己
    if username.lower() == current_user.lower():
        flash('不能删除自己的账户', 'error')
        return redirect(url_for('auth.user_management'))
    
    # 从白名单中移除用户
    success = auth_manager.remove_user_from_whitelist(username)
    
    if success:
        flash(f'成功移除用户 {username}', 'success')
    else:
        flash('移除用户失败', 'error')
    
    return redirect(url_for('auth.user_management'))
