from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from config import config
from api.github_service import GitHubService
from utils.helpers import (
    load_repos, add_repo, remove_repo, 
    format_datetime, render_markdown, truncate_text, get_label_style
)
from utils.data_exporter import DataExporter
# 导入蓝图
from api.repos import repos_bp
from api.issues import issues_bp
from api.comments import comments_bp
from api.auth import auth_bp
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
    
    # 注册蓝图
    app.register_blueprint(repos_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(auth_bp)
    
    def get_github_service():
        """获取当前用户的 GitHub 服务实例"""
        from flask import session
        github_token = session.get('github_token')
        if not github_token:
            return None
        return GitHubService(github_token)
    
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
        from flask import session
        from utils.storage import StorageManager
        
        # 检查用户是否已登录
        if 'github_token' not in session or 'username' not in session:
            return redirect(url_for('auth.login_page'))
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            session.clear()
            session['login_error'] = 'GitHub 服务不可用，请重新登录'
            return redirect(url_for('auth.login_page'))
        
        # 验证 Token 是否仍然有效
        success, _ = github_service.validate_token()
        if not success:
            session.clear()
            session['login_error'] = 'GitHub Token 已失效，请重新登录'
            return redirect(url_for('auth.login_page'))
        
        # 获取仓库数据
        storage = StorageManager()
        repos_data = storage.get_repos()
        
        # 🎯 如果仓库列表为空，自动添加默认演示仓库
        if not repos_data.get('repositories'):
            username = session.get('username')
            print(f"📝 用户 {username} 没有仓库，尝试添加默认仓库...")
            default_repo_url = 'https://github.com/anzchy/jack-notes'
            
            try:
                # 获取默认仓库信息
                result = github_service.get_repo_info(default_repo_url)
                
                if result['success']:
                    from datetime import datetime
                    
                    # 添加元数据
                    result['data']['added_at'] = datetime.now().isoformat()
                    result['data']['added_by'] = username
                    result['data']['is_default'] = True  # 标记为默认仓库
                    
                    # 添加到仓库列表
                    if 'repositories' not in repos_data:
                        repos_data['repositories'] = []
                    
                    repos_data['repositories'].append(result['data'])
                    
                    if storage.save_repos(repos_data):
                        print(f"✅ 默认仓库 {default_repo_url} 添加成功")
                    else:
                        print(f"❌ 保存默认仓库失败")
                else:
                    print(f"⚠️ 获取默认仓库信息失败: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ 添加默认仓库时出错: {e}")
                import traceback
                traceback.print_exc()
        
        # 获取用户数据
        user_data = {
            'username': session.get('username'),
            'is_admin': session.get('is_admin', False)
        }
        
        return render_template('index.html', repos=repos_data.get('repositories', []), user=user_data)
    
    @app.route('/config')
    def config_page():
        """配置页面"""
        return render_template('config.html')
    
    @app.route('/add_repo', methods=['POST'])
    def add_repository():
        """添加仓库"""
        from utils.storage import StorageManager
        from datetime import datetime
        from flask import session
        
        repo_url = request.form.get('repo_url', '').strip()
        
        # 调试信息
        print(f"🔍 正在添加仓库: {repo_url}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"X-Requested-With: {request.headers.get('X-Requested-With')}")
        print(f"Accept: {request.headers.get('Accept')}")
        
        is_ajax = (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
                  'application/json' in request.headers.get('Accept', ''))
        
        print(f"is_ajax: {is_ajax}")
        
        if not repo_url:
            print(f"❌ 错误: 仓库 URL 为空")
            if is_ajax:
                return jsonify({'success': False, 'error': '请输入仓库 URL'}), 400
            flash('请输入仓库 URL', 'error')
            return redirect(url_for('index'))
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            print(f"❌ 错误: GitHub 服务不可用")
            if is_ajax:
                return jsonify({'success': False, 'error': '请先登录'}), 401
            session['login_error'] = '请先登录'
            return redirect(url_for('auth.login_page'))
        
        # 获取仓库信息
        print(f"🔍 正在获取仓库信息: {repo_url}")
        result = github_service.get_repo_info(repo_url)
        if not result['success']:
            print(f"❌ 错误: 获取仓库信息失败 - {result['error']}")
            if is_ajax:
                return jsonify({'success': False, 'error': f'获取仓库信息失败: {result["error"]}'}), 400
            flash(f'获取仓库信息失败: {result["error"]}', 'error')
            return redirect(url_for('index'))
        
        print(f"✅ 获取到仓库信息: {result['data'].get('full_name')}")
        
        # 使用 StorageManager 添加仓库
        storage = StorageManager()
        repos_data = storage.get_repos()
        
        # 检查是否已存在
        for repo in repos_data.get('repositories', []):
            if repo.get('full_name') == result['data']['full_name']:
                print(f"⚠️ 仓库已存在: {result['data']['full_name']}")
                if is_ajax:
                    return jsonify({'success': False, 'error': '仓库已存在'}), 400
                flash('仓库已存在', 'error')
                return redirect(url_for('index'))
        
        # 添加时间戳和用户信息
        result['data']['added_at'] = datetime.now().isoformat()
        result['data']['added_by'] = session.get('username', '')
        
        print(f"📝 仓库将被添加: {result['data']['full_name']}, 添加人: {result['data']['added_by']}")
        
        # 确保 repositories 列表存在
        if 'repositories' not in repos_data:
            repos_data['repositories'] = []
        
        repos_data['repositories'].append(result['data'])
        
        # 保存到存储
        print(f"💾 正在保存仓库数据...")
        save_success = storage.save_repos(repos_data)
        
        if save_success:
            print(f"✅ 仓库保存成功: {result['data']['full_name']}")
            if is_ajax:
                print(f"📤 返回 JSON 响应: success=True")
                return jsonify({'success': True, 'message': '仓库添加成功', 'repo': result['data']})
            else:
                flash('仓库添加成功', 'success')
                return redirect(url_for('index'))
        else:
            print(f"❌ 错误: 保存仓库信息失败")
            if is_ajax:
                print(f"📤 返回 JSON 响应: success=False")
                return jsonify({'success': False, 'error': '保存仓库信息失败'}), 500
            else:
                flash('保存仓库信息失败', 'error')
                return redirect(url_for('index'))
    
    @app.route('/remove_repo/<path:repo_full_name>')
    def remove_repository(repo_full_name):
        """删除仓库"""
        from utils.storage import StorageManager
        
        storage = StorageManager()
        repos_data = storage.get_repos()
        original_count = len(repos_data.get('repositories', []))
        
        repos_data['repositories'] = [
            repo for repo in repos_data.get('repositories', [])
            if repo.get('full_name') != repo_full_name
        ]
        
        if len(repos_data['repositories']) < original_count:
            if storage.save_repos(repos_data):
                flash('仓库删除成功', 'success')
            else:
                flash('保存更改失败', 'error')
        else:
            flash('仓库不存在', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/repo/<path:repo_full_name>/issues')
    def repo_issues(repo_full_name):
        """显示仓库的 Issues"""
        page = request.args.get('page', 1, type=int)
        state = request.args.get('state', 'all')
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            session['login_error'] = '请先登录'
            return redirect(url_for('auth.login_page'))
        
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
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            session['login_error'] = '请先登录'
            return redirect(url_for('auth.login_page'))
        
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
    @app.route('/api/my_repos')
    def api_my_repos():
        """获取当前用户的仓库列表（前端渲染专用）"""
        from flask import session
        from utils.storage import StorageManager
        
        # 1. 获取用户信息
        username = session.get('username')
        is_admin = session.get('is_admin', False)
        
        if not username:
            return jsonify({'success': False, 'error': '未登录'}), 401
            
        # 2. 获取数据
        storage = StorageManager()
        # 使用我们刚刚修复过的、忽略大小写的权限逻辑
        repos_data = storage.get_user_repos(username, is_admin)
        
        repos = repos_data.get('repositories', [])
        
        # 3. 返回 JSON
        return jsonify({
            'success': True,
            'count': len(repos),
            'username': username,
            'is_admin': is_admin,
            'repositories': repos
        })

    @app.route('/api/repos')
    def api_repos():
        """获取仓库列表 API (旧接口，保留兼容性)"""
        return api_my_repos()
    
    @app.route('/api/repo/<path:repo_full_name>/issues')
    def api_repo_issues(repo_full_name):
        """获取仓库 Issues API"""
        page = request.args.get('page', 1, type=int)
        state = request.args.get('state', 'all')
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
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
    
    @app.route('/api/config', methods=['GET'])
    def api_get_config():
        """获取配置信息"""
        from flask import session
        github_service = get_github_service()
        token_valid = bool(github_service and github_service.validate_token()[0]) if github_service else False
        
        return jsonify({
            'has_token': bool(session.get('github_token')),
            'token_valid': token_valid
        })
    
    @app.route('/api/user', methods=['GET'])
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
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
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
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
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
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        result = github_service.update_comment(repo_full_name, comment_id, data['body'])
        return jsonify(result)
    
    # 删除评论路由已移至 api/comments.py
    
    @app.route('/api/export/repos', methods=['GET'])
    def api_get_exportable_repos():
        """获取可导出的仓库列表"""
        try:
            exporter = DataExporter(get_github_token())
            repos = exporter.get_available_repos()
            return jsonify({
                'success': True,
                'repos': repos
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'获取仓库列表失败: {str(e)}'
            }), 500
    
    @app.route('/api/export/<path:repo_full_name>', methods=['POST'])
    def api_export_repo_data(repo_full_name):
        """导出仓库数据"""
        try:
            data = request.get_json() or {}
            export_format = data.get('format', 'json').lower()
            
            # 验证导出格式
            if export_format not in ['json', 'csv']:
                return jsonify({
                    'success': False,
                    'error': f'不支持的导出格式: {export_format}'
                }), 400
            
            # 执行导出
            exporter = DataExporter(get_github_token())
            result = exporter.export_repo_data(repo_full_name, export_format)
            
            if not result.get('success'):
                return jsonify(result), 400
            
            # 返回文件内容
            from flask import Response
            response = Response(
                result['content'],
                mimetype=result['content_type'],
                headers={
                    'Content-Disposition': f'attachment; filename="{result["filename"]}"',
                    'Content-Type': result['content_type']
                }
            )
            return response
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'导出数据时发生错误: {str(e)}'
            }), 500
    
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
    app.run(debug=True, host='0.0.0.0', port=8888)