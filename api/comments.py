from flask import Blueprint, request, jsonify, session
from services.github_service import GitHubService
from utils.auth import AuthManager
import os

# 创建蓝图
comments_bp = Blueprint('comments', __name__)

# 初始化服务
auth_manager = AuthManager()

def get_github_service():
    """获取当前用户的 GitHub 服务实例"""
    github_token = session.get('github_token')
    if not github_token:
        return None
    return GitHubService(github_token)

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments', methods=['GET'])
def api_get_comments(repo_full_name, issue_number):
    """获取 Issue 的所有评论"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.get_issue_comments(repo_full_name, issue_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取评论失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments', methods=['POST'])
def api_create_comment(repo_full_name, issue_number):
    """创建新评论"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'body' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    body = data.get('body', '').strip()
    if not body:
        return jsonify({
            'success': False,
            'error': '评论内容不能为空'
        }), 400
    
    try:
        result = github_service.create_comment(repo_full_name, issue_number, body)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'创建评论失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/comments/<int:comment_id>', methods=['GET'])
def api_get_comment(repo_full_name, comment_id):
    """获取单个评论详情"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.get_comment(repo_full_name, comment_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取评论失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/comments/<int:comment_id>', methods=['PUT'])
def api_update_comment(repo_full_name, comment_id):
    """更新评论内容"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'body' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    body = data.get('body', '').strip()
    if not body:
        return jsonify({
            'success': False,
            'error': '评论内容不能为空'
        }), 400
    
    try:
        result = github_service.update_comment(repo_full_name, comment_id, body)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新评论失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/comments/<int:comment_id>', methods=['DELETE'])
def api_delete_comment(repo_full_name, comment_id):
    """删除评论"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.delete_comment(repo_full_name, comment_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除评论失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments/<int:comment_id>/reactions', methods=['POST'])
def api_add_reaction(repo_full_name, issue_number, comment_id):
    """添加评论反应（表情）"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    content = data.get('content', '').strip()
    if not content:
        return jsonify({
            'success': False,
            'error': '反应内容不能为空'
        }), 400
    
    # 验证反应类型
    valid_reactions = ['+1', '-1', 'laugh', 'confused', 'heart', 'hooray', 'rocket', 'eyes']
    if content not in valid_reactions:
        return jsonify({
            'success': False,
            'error': f'无效的反应类型: {content}'
        }), 400
    
    try:
        result = github_service.add_reaction(repo_full_name, comment_id, content)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'添加反应失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments/<int:comment_id>/reactions/<content>', methods=['DELETE'])
def api_remove_reaction(repo_full_name, issue_number, comment_id, content):
    """移除评论反应"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.remove_reaction(repo_full_name, comment_id, content)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'移除反应失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments/<int:comment_id>/reactions', methods=['GET'])
def api_get_reactions(repo_full_name, issue_number, comment_id):
    """获取评论的所有反应"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        result = github_service.get_reactions(repo_full_name, comment_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取反应失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments/<int:comment_id>/replies', methods=['POST'])
def api_create_reply(repo_full_name, issue_number, comment_id):
    """回复评论（创建新评论并引用原评论）"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    data = request.get_json()
    if not data or 'body' not in data:
        return jsonify({
            'success': False,
            'error': '缺少必要的参数'
        }), 400
    
    body = data.get('body', '').strip()
    if not body:
        return jsonify({
            'success': False,
            'error': '回复内容不能为空'
        }), 400
    
    # 添加引用格式
    referenced_body = f"> {body}"
    
    try:
        result = github_service.create_comment(repo_full_name, issue_number, referenced_body)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'创建回复失败: {str(e)}'
        }), 500

@comments_bp.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments/<int:comment_id>/edit-history', methods=['GET'])
def api_get_comment_edit_history(repo_full_name, issue_number, comment_id):
    """获取评论编辑历史（如果 GitHub API 支持）"""
    github_service = get_github_service()
    if not github_service:
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401
    
    try:
        # 注意：GitHub API 可能不直接支持评论编辑历史
        # 这里返回基本信息，实际实现可能需要其他方式
        result = github_service.get_comment(repo_full_name, comment_id)
        if result['success']:
            comment_data = result['data']
            return jsonify({
                'success': True,
                'data': {
                    'comment_id': comment_id,
                    'created_at': comment_data.get('created_at'),
                    'updated_at': comment_data.get('updated_at'),
                    'edited': comment_data.get('created_at') != comment_data.get('updated_at'),
                    'edit_count': 1 if comment_data.get('created_at') != comment_data.get('updated_at') else 0
                }
            })
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取编辑历史失败: {str(e)}'
        }), 500
