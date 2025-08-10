from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from config import config
from api.github_service import GitHubService
from utils.helpers import (
    load_repos, add_repo, remove_repo, 
    format_datetime, render_markdown, truncate_text, get_label_style
)
import os
import sys
import json
from pathlib import Path

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持 PyInstaller 打包"""
    try:
        # PyInstaller 创建临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_user_config_path():
    """获取用户配置文件路径"""
    home = Path.home()
    config_dir = home / '.hubnote'
    config_dir.mkdir(exist_ok=True)
    return config_dir / 'config.json'

def load_user_config():
    """加载用户配置"""
    config_path = get_user_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    return {}

def save_user_config(config):
    """保存用户配置"""
    config_path = get_user_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False

def get_github_token():
    """获取 GitHub Token，优先从用户配置读取，然后从环境变量读取"""
    # 首先尝试从用户配置文件读取
    user_config = load_user_config()
    if 'github_token' in user_config and user_config['github_token']:
        return user_config['github_token']
    
    # 然后尝试从环境变量读取
    return os.getenv('GITHUB_TOKEN')

def create_app(config_name=None):
    # 设置模板和静态文件路径
    template_folder = get_resource_path('templates')
    static_folder = get_resource_path('static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    # 配置
    config_name = config_name or os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 启用 CORS
    CORS(app)
    
    # 初始化 GitHub 服务
    github_token = get_github_token()
    github_service = GitHubService(github_token)
    
    # 模板过滤器
    @app.template_filter('datetime')
    def datetime_filter(s):
        return format_datetime(s)
    
    @app.template_filter('markdown')
    def markdown_filter(s):
        return render_markdown(s)
    
    @app.template_filter('truncate')
    def truncate_filter(s, length=100):
        return truncate_text(s, length)
    
    @app.template_filter('label_style')
    def label_style_filter(color):
        return get_label_style(color)
    
    # 路由
    @app.route('/')
    def index():
        """主页 - 显示仓库列表"""
        # 检查是否有有效的 GitHub Token
        if not github_service.token:
            return redirect(url_for('config_page'))
        
        # 验证 Token 是否有效
        success, _ = github_service.validate_token()
        if not success:
            flash('GitHub Token 无效，请重新配置', 'error')
            return redirect(url_for('config_page'))
        
        repos_data = load_repos()
        return render_template('index.html', repos=repos_data['repositories'])
    
    @app.route('/config')
    def config_page():
        """配置页面"""
        return render_template('config.html')
    
    @app.route('/add_repo', methods=['POST'])
    def add_repository():
        """添加仓库"""
        repo_url = request.form.get('repo_url', '').strip()
        if not repo_url:
            flash('请输入仓库 URL', 'error')
            return redirect(url_for('index'))
        
        # 获取仓库信息
        result = github_service.get_repo_info(repo_url)
        if not result['success']:
            flash(f'获取仓库信息失败: {result["error"]}', 'error')
            return redirect(url_for('index'))
        
        # 添加仓库
        success, message = add_repo(result['data'])
        flash(message, 'success' if success else 'error')
        return redirect(url_for('index'))
    
    @app.route('/remove_repo/<path:repo_full_name>')
    def remove_repository(repo_full_name):
        """删除仓库"""
        success, message = remove_repo(repo_full_name)
        flash(message, 'success' if success else 'error')
        return redirect(url_for('index'))
    
    @app.route('/repo/<path:repo_full_name>/issues')
    def repo_issues(repo_full_name):
        """显示仓库的 Issues"""
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
            flash(f'获取 Issues 失败: {result["error"]}', 'error')
            return redirect(url_for('index'))
        
        return render_template('issues.html', 
                             repo_name=repo_full_name,
                             issues=result['data'],
                             current_page=page,
                             state=state)
    
    @app.route('/repo/<path:repo_full_name>/issue/<int:issue_number>')
    def issue_detail(repo_full_name, issue_number):
        """显示 Issue 详情"""
        # 获取 Issue 详情
        issue_result = github_service.get_issue_detail(repo_full_name, issue_number)
        if not issue_result['success']:
            flash(f'获取 Issue 详情失败: {issue_result["error"]}', 'error')
            return redirect(url_for('repo_issues', repo_full_name=repo_full_name))
        
        # 获取评论
        comments_result = github_service.get_issue_comments(repo_full_name, issue_number)
        comments = comments_result['data'] if comments_result['success'] else []
        
        return render_template('issue_detail.html',
                             repo_name=repo_full_name,
                             issue=issue_result['data'],
                             comments=comments)
    
    # API 路由
    @app.route('/api/repos')
    def api_repos():
        """获取仓库列表 API"""
        repos_data = load_repos()
        return jsonify(repos_data)
    
    @app.route('/api/repo/<path:repo_full_name>/issues')
    def api_repo_issues(repo_full_name):
        """获取仓库 Issues API"""
        page = request.args.get('page', 1, type=int)
        state = request.args.get('state', 'all')
        
        result = github_service.get_issues(
            repo_full_name, 
            state=state, 
            page=page, 
            per_page=20
        )
        return jsonify(result)
    
    @app.route('/api/validate_token')
    def api_validate_token():
        """验证 GitHub Token"""
        success, message = github_service.validate_token()
        return jsonify({
            'success': success,
            'message': message
        })
    
    @app.route('/api/config', methods=['GET'])
    def api_get_config():
        """获取配置信息"""
        user_config = load_user_config()
        return jsonify({
            'has_token': bool(user_config.get('github_token')),
            'token_valid': bool(github_service.token and github_service.validate_token()[0])
        })
    
    @app.route('/api/user', methods=['GET'])
    def api_get_current_user():
        """获取当前用户信息"""
        if not github_service.token:
            return jsonify({
                'success': False,
                'error': '未配置 GitHub Token'
            }), 401
        
        result = github_service.get_current_user()
        return jsonify(result)
    
    @app.route('/api/config/token', methods=['POST'])
    def api_save_token():
        """保存 GitHub Token"""
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'success': False, 'message': 'Token 不能为空'}), 400
        
        # 验证 token
        temp_service = GitHubService(token)
        success, message = temp_service.validate_token()
        
        if not success:
            return jsonify({'success': False, 'message': f'Token 验证失败: {message}'}), 400
        
        # 保存配置
        user_config = load_user_config()
        user_config['github_token'] = token
        
        if save_user_config(user_config):
            # 更新当前服务的 token
            github_service.token = token
            return jsonify({'success': True, 'message': 'Token 保存成功'})
        else:
            return jsonify({'success': False, 'message': '保存配置失败'}), 500
    
    @app.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>', methods=['PATCH'])
    def api_update_issue(repo_full_name, issue_number):
        """更新 Issue 内容"""
        data = request.get_json()
        if not data or 'body' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要的参数'
            }), 400
        
        result = github_service.update_issue(repo_full_name, issue_number, data['body'])
        return jsonify(result)
    
    @app.route('/api/repos/<path:repo_full_name>/issues/<int:issue_number>/comments', methods=['POST'])
    def api_create_comment(repo_full_name, issue_number):
        """创建新评论"""
        data = request.get_json()
        if not data or 'body' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要的参数'
            }), 400
        
        result = github_service.create_comment(repo_full_name, issue_number, data['body'])
        return jsonify(result)
    
    @app.route('/api/repos/<path:repo_full_name>/issues/comments/<int:comment_id>', methods=['PATCH'])
    def api_update_comment(repo_full_name, comment_id):
        """更新评论内容"""
        data = request.get_json()
        if not data or 'body' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要的参数'
            }), 400
        
        result = github_service.update_comment(repo_full_name, comment_id, data['body'])
        return jsonify(result)
    
    @app.route('/api/repos/<path:repo_full_name>/issues/comments/<int:comment_id>', methods=['DELETE'])
    def api_delete_comment(repo_full_name, comment_id):
        """删除评论"""
        result = github_service.delete_comment(repo_full_name, comment_id)
        return jsonify(result)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)