from flask import Blueprint, request, jsonify, flash, redirect, url_for, session
from services.github_service import GitHubService
from utils.storage import StorageManager
from utils.auth import AuthManager
import os

# 创建蓝图
repos_bp = Blueprint('repos', __name__)

# 初始化服务
storage = StorageManager()
auth_manager = AuthManager()

def get_github_service():
    """获取当前用户的 GitHub 服务实例"""
    github_token = session.get('github_token')
    if not github_token:
        return None
    return GitHubService(github_token)

@repos_bp.route('/add_repo', methods=['POST'])
def add_repository():
    """添加仓库"""
    # 检查是否为 AJAX 请求
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' or
        'application/json' in request.headers.get('Accept', '')
    )
    
    # 检查登录状态
    if 'github_token' not in session:
        if is_ajax:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        flash('请先登录', 'error')
        return redirect(url_for('auth.login_page'))
    
    repo_url = request.form.get('repo_url', '').strip()
    if not repo_url:
        if is_ajax:
            return jsonify({
                'success': False,
                'error': '请输入仓库 URL'
            }), 400
        flash('请输入仓库 URL', 'error')
        return redirect(url_for('index'))
    
    # 获取 GitHub 服务实例
    github_service = get_github_service()
    if not github_service:
        if is_ajax:
            return jsonify({
                'success': False,
                'error': 'GitHub 服务不可用，请重新登录'
            }), 401
        session['login_error'] = 'GitHub 服务不可用，请重新登录'
        return redirect(url_for('auth.login_page'))
    
    # 获取仓库信息
    result = github_service.get_repo_info(repo_url)
    if not result['success']:
        if is_ajax:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        flash(f'获取仓库信息失败: {result["error"]}', 'error')
        return redirect(url_for('index'))
    
    # 添加仓库
    success, message = _add_repo(result['data'])
    
    if is_ajax:
        return jsonify({
            'success': success,
            'message': message,
            'repo': result['data'] if success else None
        })
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('index'))

@repos_bp.route('/remove_repo/<path:repo_full_name>')
def remove_repository(repo_full_name):
    """删除仓库"""
    # 检查登录状态
    if 'github_token' not in session:
        session['login_error'] = '请先登录'
        return redirect(url_for('auth.login_page'))
    
    success, message = _remove_repo(repo_full_name)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('index'))

@repos_bp.route('/api/repos', methods=['GET'])
def api_get_repos():
    """获取仓库列表 API"""
    repos_data = storage.get_repos()
    return jsonify(repos_data)

@repos_bp.route('/api/repos', methods=['POST'])
def api_create_repo():
    """创建仓库 API"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'repo_url' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    repo_url = data['repo_url'].strip()
    
    # 获取仓库信息
    result = github_service.get_repo_info(repo_url)
    if not result['success']:
        return jsonify({
            'success': False,
            'error': result['error']
        }), 400
    
    # 添加仓库
    success, message = _add_repo(result['data'])
    return jsonify({
        'success': success,
        'message': message,
        'data': result['data'] if success else None
    })

@repos_bp.route('/api/repos/<path:repo_full_name>', methods=['DELETE'])
def api_delete_repo(repo_full_name):
    """删除仓库 API"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    success, message = _remove_repo(repo_full_name)
    return jsonify({
        'success': success,
        'message': message
    })

@repos_bp.route('/api/repos/<path:repo_full_name>/info', methods=['GET'])
def api_get_repo_info(repo_full_name):
    """获取仓库详细信息 API"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.get_repo_info(repo_full_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取仓库信息失败: {str(e)}'
        }), 500

def _add_repo(repo_info):
    """添加仓库到存储"""
    repos_data = storage.get_repos()
    
    # 检查是否已存在
    for repo in repos_data.get('repositories', []):
        if repo.get('full_name') == repo_info['full_name']:
            return False, '仓库已存在'
    
    # 添加时间戳
    from datetime import datetime
    repo_info['added_at'] = datetime.now().isoformat()
    
    # 确保 repositories 列表存在
    if 'repositories' not in repos_data:
        repos_data['repositories'] = []
    
    repos_data['repositories'].append(repo_info)
    
    # 保存到存储
    if storage.save_repos(repos_data):
        return True, '仓库添加成功'
    else:
        return False, '保存仓库信息失败'

def _remove_repo(repo_full_name):
    """从存储中移除仓库"""
    repos_data = storage.get_repos()
    original_count = len(repos_data.get('repositories', []))
    
    repos_data['repositories'] = [
        repo for repo in repos_data.get('repositories', [])
        if repo.get('full_name') != repo_full_name
    ]
    
    if len(repos_data['repositories']) < original_count:
        if storage.save_repos(repos_data):
            return True, '仓库删除成功'
        else:
            return False, '保存更改失败'
    return False, '仓库不存在'
