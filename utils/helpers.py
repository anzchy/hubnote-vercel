import json
import os
from datetime import datetime
import markdown

def load_repos():
    """加载仓库列表"""
    repos_file = 'data/repos.json'
    if os.path.exists(repos_file):
        with open(repos_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'repositories': []}

def save_repos(repos_data):
    """保存仓库列表"""
    repos_file = 'data/repos.json'
    os.makedirs(os.path.dirname(repos_file), exist_ok=True)
    with open(repos_file, 'w', encoding='utf-8') as f:
        json.dump(repos_data, f, indent=2, ensure_ascii=False)

def add_repo(repo_info):
    """添加仓库到列表"""
    repos_data = load_repos()
    
    # 检查是否已存在
    for repo in repos_data['repositories']:
        if repo['full_name'] == repo_info['full_name']:
            return False, '仓库已存在'
    
    # 添加时间戳
    repo_info['added_at'] = datetime.now().isoformat()
    repos_data['repositories'].append(repo_info)
    save_repos(repos_data)
    return True, '仓库添加成功'

def remove_repo(repo_full_name):
    """从列表中移除仓库"""
    repos_data = load_repos()
    original_count = len(repos_data['repositories'])
    
    repos_data['repositories'] = [
        repo for repo in repos_data['repositories'] 
        if repo['full_name'] != repo_full_name
    ]
    
    if len(repos_data['repositories']) < original_count:
        save_repos(repos_data)
        return True, '仓库删除成功'
    return False, '仓库不存在'

def format_datetime(iso_string):
    """格式化日期时间"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
    except:
        return iso_string

def render_markdown(text):
    """渲染 Markdown 文本"""
    if not text:
        return ''
    
    md = markdown.Markdown(extensions=[
        'codehilite',
        'fenced_code',
        'tables',
        'toc'
    ])
    html_content = md.convert(text)
    
    # 修复链接问题
    import re
    
    # 1. 移除错误的本地路径前缀
    pattern = r'href="http://127\.0\.0\.1:5000/repo/[^/]+/[^/]+/issue/([^"]+)"'
    html_content = re.sub(pattern, r'href="\1"', html_content)
    
    # 2. 为看起来像域名但没有协议的链接添加https://前缀
    # 匹配形如 href="domain.com" 或 href="subdomain.domain.com" 的链接
    domain_pattern = r'href="([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)"'
    def add_https_protocol(match):
        url = match.group(1)
        # 如果已经有协议，不处理
        if url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            return match.group(0)
        # 添加https://前缀
        return f'href="https://{url}"'
    
    html_content = re.sub(domain_pattern, add_https_protocol, html_content)
    
    return html_content

def truncate_text(text, max_length=100):
    """截断文本"""
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

def get_label_style(color):
    """根据标签颜色生成样式"""
    # 简单的颜色对比度计算
    if color:
        # 将十六进制颜色转换为 RGB
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            # 计算亮度
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = '#000' if brightness > 128 else '#fff'
            return f'background-color: #{color}; color: {text_color};'
        except:
            return 'background-color: #e1e4e8; color: #586069;'
    return 'background-color: #e1e4e8; color: #586069;'