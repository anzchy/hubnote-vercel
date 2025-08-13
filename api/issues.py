from flask import Blueprint, request, jsonify, render_template, session
from services.github_service import GitHubService
from utils.auth import AuthManager
import os

# 创建蓝图
issues_bp = Blueprint('issues', __name__)

# 初始化服务
auth_manager = AuthManager()

def get_github_service():
    """获取当前用户的 GitHub 服务实例"""
    github_token = session.get('github_token')
    if not github_token:
        return None
    return GitHubService(github_token)

@issues_bp.route('/repo/<path:repo_full_name>/issues')
def repo_issues(repo_full_name):
    """显示仓库的 Issues"""
    github_service = get_github_service()
    if not github_service:
        return render_template('issues.html', 
                             repo_name=repo_full_name,
                             issues=[],
                             current_page=1,
                             state='all',
                             error='请先登录')
    
    page = request.args.get('page', 1, type=int)
    state = request.args.get('state', 'all')
    
    # 获取 Issues
    result = github_service.get_issues(
        repo_full_name, 
        state=state, 
        page=page, 
        per_page=20
    )
    
    if not result['success']:
        return render_template('issues.html', 
                             repo_name=repo_full_name,
                             issues=[],
                             current_page=page,
                             state=state,
                             error=result['error'])
    
    return render_template('issues.html', 
                         repo_name=repo_full_name,
                         issues=result['data'],
                         current_page=page,
                         state=state)

@issues_bp.route('/repo/<path:repo_full_name>/issue/<int:issue_number>')
def issue_detail(repo_full_name, issue_number):
    """显示 Issue 详情"""
    github_service = get_github_service()
    if not github_service:
        return render_template('issue_detail.html',
                             repo_name=repo_full_name,
                             issue=None,
                             comments=[],
                             error='请先登录')
    
    # 获取 Issue 详情
    issue_result = github_service.get_issue_detail(repo_full_name, issue_number)
    if not issue_result['success']:
        return render_template('issue_detail.html',
                             repo_name=repo_full_name,
                             issue=None,
                             comments=[],
                             error=issue_result['error'])
    
    # 获取评论
    comments_result = github_service.get_issue_comments(repo_full_name, issue_number)
    comments = comments_result['data'] if comments_result['success'] else []
    
    return render_template('issue_detail.html',
                         repo_name=repo_full_name,
                         issue=issue_result['data'],
                         comments=comments)

@issues_bp.route('/repo/<path:repo_full_name>/issue/create', methods=['GET'])
def issue_create_page(repo_full_name):
    """Issue 创建页面"""
    return render_template('issue_create.html', repo_name=repo_full_name)

@issues_bp.route('/repo/<path:repo_full_name>/issue/<int:issue_number>/edit', methods=['GET'])
def issue_edit_page(repo_full_name, issue_number):
    """Issue 编辑页面"""
    github_service = get_github_service()
    if not github_service:
        return render_template('issue_edit.html',
                             repo_name=repo_full_name,
                             issue=None,
                             error='请先登录')
    
    # 获取 Issue 详情
    issue_result = github_service.get_issue_detail(repo_full_name, issue_number)
    if not issue_result['success']:
        return render_template('issue_edit.html',
                             repo_name=repo_full_name,
                             issue=None,
                             error=issue_result['error'])
    
    return render_template('issue_edit.html',
                         repo_name=repo_full_name,
                         issue=issue_result['data'])

# API 路由
@issues_bp.route('/api/repos/<path:repo_full_name>/issues', methods=['GET'])
def api_get_issues(repo_full_name):
    """获取仓库 Issues API"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    page = request.args.get('page', 1, type=int)
    state = request.args.get('state', 'all')
    
    result = github_service.get_issues(
        repo_full_name, 
        state=state, 
        page=page, 
        per_page=20
    )
    return jsonify(result)

@issues_bp.route('/api/repos/<path:repo_full_name>/issues', methods=['POST'])
def api_create_issue(repo_full_name):
    """创建新的 Issue"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    title = data.get('title', '').strip()
    body = data.get('body', '').strip()
    labels = data.get('labels', [])
    assignees = data.get('assignees', [])
    
    if not title:
        return jsonify({
            'success': False,
            'error': 'Issue 标题不能为空'
        }), 400
    
    try:
        result = github_service.create_issue(
            repo_full_name, 
            title, 
            body, 
            labels, 
            assignees
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'创建 Issue 失败: {str(e)}'
        }), 500

@issues_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>', methods=['GET'])
def api_get_issue_detail(repo_full_name, issue_number):
    """获取 Issue 详情 API"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    result = github_service.get_issue_detail(repo_full_name, issue_number)
    return jsonify(result)

@issues_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>', methods=['PUT'])
def api_update_issue(repo_full_name, issue_number):
    """更新 Issue"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    try:
        result = github_service.update_issue(
            repo_full_name, 
            issue_number, 
            data
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新 Issue 失败: {str(e)}'
        }), 500

@issues_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>', methods=['DELETE'])
def api_delete_issue(repo_full_name, issue_number):
    """删除 Issue"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.delete_issue(repo_full_name, issue_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除 Issue 失败: {str(e)}'
        }), 500

@issues_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/close', methods=['POST'])
def api_close_issue(repo_full_name, issue_number):
    """关闭 Issue"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.close_issue(repo_full_name, issue_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'关闭 Issue 失败: {str(e)}'
        }), 500

@issues_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/reopen', methods=['POST'])
def api_reopen_issue(repo_full_name, issue_number):
    """重新打开 Issue"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.reopen_issue(repo_full_name, issue_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'重新打开 Issue 失败: {str(e)}'
        }), 500

@issues_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/labels', methods=['POST'])
def api_update_issue_labels(repo_full_name, issue_number):
    """更新 Issue 标签"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'labels' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    try:
        result = github_service.update_issue_labels(
            repo_full_name, 
            issue_number, 
            data['labels']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新 Issue 标签失败: {str(e)}'
        }), 500

@issues_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/assignees', methods=['POST'])
def api_update_issue_assignees(repo_full_name, issue_number):
    """更新 Issue 分配者"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'assignees' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    try:
        result = github_service.update_issue_assignees(
            repo_full_name, 
            issue_number, 
            data['assignees']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新 Issue 分配者失败: {str(e)}'
        }), 500
