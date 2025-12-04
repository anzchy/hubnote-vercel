from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, session
from flask_cors import CORS
import os
import sys
from pathlib import Path
from github import Github

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.github_service import GitHubService
from utils.storage import StorageManager
from utils.auth import AuthManager
from utils.helpers import format_datetime, render_markdown, truncate_text, get_label_style

# 导入蓝图
from api.repos import repos_bp
from api.issues import issues_bp
from api.comments import comments_bp
from api.auth import auth_bp

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持 Vercel 部署"""
    try:
        # Vercel 环境下的路径处理
        base_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(os.path.dirname(base_path), relative_path)
    except Exception:
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

def create_app():
    """创建 Flask 应用"""
    # 设置模板和静态文件路径
    template_folder = get_resource_path('templates')
    static_folder = get_resource_path('static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vercel-secret-key')
    app.config['DEBUG'] = False  # Vercel 生产环境
    
    # 启用 CORS
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(repos_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(auth_bp)
    
    # 初始化服务
    storage = StorageManager()
    auth_manager = AuthManager()
    
    def get_github_service():
        """获取当前用户的 GitHub 服务实例"""
        github_token = session.get('github_token')
        if not github_token:
            return None
        return GitHubService(github_token)
    
    def _add_repo(repo_data):
        """添加仓库到存储（内部函数）"""
        from datetime import datetime
        from flask import session
        
        # 使用 StorageManager
        storage = StorageManager()
        repos_data = storage.get_repos()
        
        # 检查是否已存在
        for repo in repos_data.get('repositories', []):
            if repo.get('full_name') == repo_data['full_name']:
                return False, '仓库已存在'
        
        # 添加元数据
        repo_data['added_at'] = datetime.now().isoformat()
        repo_data['added_by'] = session.get('username', '')
        
        # 确保列表存在
        if 'repositories' not in repos_data:
            repos_data['repositories'] = []
            
        repos_data['repositories'].append(repo_data)
        
        # 保存
        if storage.save_repos(repos_data):
            return True, '仓库添加成功'
        else:
            return False, '保存仓库信息失败'

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
    
    # 主页路由
    @app.route('/')
    def index():
        """主页 - 显示仓库列表"""
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
        
        # 获取用户信息
        username = session.get('username')
        is_admin = session.get('is_admin', False)
        
        # 根据用户权限获取仓库列表
        repos_data = storage.get_user_repos(username, is_admin)
        
        # 🎯 如果用户仓库为空，自动添加默认演示仓库
        if not repos_data.get('repositories'):
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
                    
                    # 获取所有仓库数据
                    all_repos = storage.get_repos()
                    if 'repositories' not in all_repos:
                        all_repos['repositories'] = []
                    
                    # 检查是否已存在
                    exists = any(r.get('full_name') == result['data']['full_name'] 
                               for r in all_repos['repositories'])
                    
                    if not exists:
                        all_repos['repositories'].append(result['data'])
                        
                        if storage.save_repos(all_repos):
                            print(f"✅ 默认仓库 {default_repo_url} 添加成功")
                            # 重新获取用户仓库（包含新添加的默认仓库）
                            repos_data = storage.get_user_repos(username, is_admin)
                        else:
                            print(f"❌ 保存默认仓库失败")
                    else:
                        print(f"ℹ️ 默认仓库已存在")
                        # 重新获取（可能其他用户添加过）
                        repos_data = storage.get_user_repos(username, is_admin)
                else:
                    print(f"⚠️ 获取默认仓库信息失败: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ 添加默认仓库时出错: {e}")
                import traceback
                traceback.print_exc()
        
        user_data = {
            'username': username,
            'is_admin': is_admin
        }
        
        # 修改：不再由后端渲染 repos，而是让前端通过 API 获取
        # 这样可以分离关注点，并更容易排查数据问题
        return render_template('index.html', 
                             repos=[],  # 传空列表，让前端 JS 去加载
                             user=user_data)

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
        repos_data = storage.get_user_repos(username, is_admin)
        
        repos = repos_data.get('repositories', [])
        
        # 4. 强制注入目标仓库（作为最后的保险措施）
        target_repo = "anzchy/jack-notes"
        has_target = any(r.get('full_name') == target_repo for r in repos)
        
        if not has_target:
            print(f"⚠️ 强制注入默认仓库: {target_repo}")
            # 手动构建一个仓库对象
            injected_repo = {
                "full_name": "anzchy/jack-notes",
                "name": "jack-notes",
                "url": "https://github.com/anzchy/jack-notes",
                "html_url": "https://github.com/anzchy/jack-notes",
                "description": "Notes and thoughts (Auto-injected)",
                "language": "Markdown",
                "stars": 0,
                "forks": 0,
                "open_issues": 0,
                "added_at": "2024-01-01T00:00:00",
                "added_by": "system",
                "is_default": True,
                "owner": "anzchy"
            }
            repos.append(injected_repo)
        
        # 3. 返回 JSON
        return jsonify({
            'success': True,
            'count': len(repos),
            'username': username,
            'is_admin': is_admin,
            'repositories': repos
        })
    
    # 设置引导页面
    @app.route('/setup')
    def setup_guide():
        """设置引导页面"""
        return render_template('setup_guide.html')
    
    # 配置页面
    @app.route('/config')
    def config_page():
        """配置页面"""
        return render_template('config.html')
    
    # 添加仓库路由
    @app.route('/add_repo', methods=['POST'])
    def add_repository():
        """添加仓库"""
        from datetime import datetime
        
        repo_url = request.form.get('repo_url', '').strip()
        
        # 检查是否为AJAX请求
        is_ajax = (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
                  'application/json' in request.headers.get('Accept', '') or
                  request.headers.get('Content-Type') == 'application/x-www-form-urlencoded')
        
        # 如果请求包含Accept: application/json，强制返回JSON
        if 'application/json' in request.headers.get('Accept', ''):
            is_ajax = True
        
        if not repo_url:
            if is_ajax:
                return jsonify({'success': False, 'error': '请输入仓库 URL'}), 400
            flash('请输入仓库 URL', 'error')
            return redirect(url_for('index'))
        
        # 获取 GitHub 服务实例
        github_service = get_github_service()
        if not github_service:
            if is_ajax:
                return jsonify({'success': False, 'error': '请先登录'}), 401
            flash('请先登录', 'error')
            return redirect(url_for('auth.login_page'))
        
        # 获取仓库信息
        result = github_service.get_repo_info(repo_url)
        if not result['success']:
            if is_ajax:
                return jsonify({'success': False, 'error': f'获取仓库信息失败: {result["error"]}'}), 400
            flash(f'获取仓库信息失败: {result["error"]}', 'error')
            return redirect(url_for('index'))
        
        # 使用 StorageManager 添加仓库
        success, message = _add_repo(result['data'])
        
        if success:
            if is_ajax:
                return jsonify({'success': True, 'message': message, 'repo': result['data']})
            flash(message, 'success')
        else:
            if is_ajax:
                return jsonify({'success': False, 'error': message}), 400
            flash(message, 'error')
        
        return redirect(url_for('index'))
    
    # 删除仓库路由
    @app.route('/remove_repo/<path:repo_full_name>')
    def remove_repository(repo_full_name):
        """删除仓库"""
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
            flash('未找到要删除的仓库', 'error')
        
        return redirect(url_for('index'))
    
    # 静态文件路由
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """提供静态文件"""
        return send_from_directory(app.static_folder, filename)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

# 创建应用实例
app = create_app()

# Vercel 入口点 - 直接导出 app 实例
# Vercel 会自动处理 WSGI 应用
app.debug = False

# 开发环境运行
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5055)
