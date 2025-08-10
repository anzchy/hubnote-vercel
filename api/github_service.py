import requests
from github import Github
from datetime import datetime
import json
import os

class GitHubService:
    def __init__(self, token=None):
        self.token = token
        self.github = Github(token) if token else Github()
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})
    
    def validate_token(self):
        """验证 GitHub Token 是否有效"""
        try:
            user = self.github.get_user()
            return True, user.login
        except Exception as e:
            return False, str(e)
    
    def get_current_user(self):
        """获取当前用户信息"""
        try:
            user = self.github.get_user()
            return {
                'success': True,
                'data': {
                    'login': user.login,
                    'avatar_url': user.avatar_url,
                    'name': user.name,
                    'email': user.email,
                    'bio': user.bio,
                    'html_url': user.html_url
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_repo_info(self, repo_url):
        """获取仓库基本信息"""
        try:
            # 从 URL 提取仓库名
            if 'github.com' in repo_url:
                parts = repo_url.strip('/').split('/')
                if len(parts) < 2:
                    return {
                        'success': False,
                        'error': f'无效的 GitHub URL 格式: {repo_url}'
                    }
                owner = parts[-2]
                repo_name = parts[-1]
            else:
                # 假设格式为 owner/repo
                if '/' not in repo_url:
                    return {
                        'success': False,
                        'error': f'无效的仓库格式，应为 owner/repo: {repo_url}'
                    }
                owner, repo_name = repo_url.split('/', 1)
            
            # 清理仓库名（移除可能的 .git 后缀）
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            
            full_name = f"{owner}/{repo_name}"
            print(f"🔍 正在获取仓库信息: {full_name}")
            
            repo = self.github.get_repo(full_name)
            
            return {
                'success': True,
                'data': {
                    'full_name': repo.full_name,
                    'name': repo.name,
                    'owner': repo.owner.login,
                    'description': repo.description,
                    'url': repo.html_url,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'language': repo.language,
                    'created_at': repo.created_at.isoformat(),
                    'updated_at': repo.updated_at.isoformat(),
                    'open_issues': repo.open_issues_count
                }
            }
        except Exception as e:
            error_msg = str(e)
            
            # 提供更友好的错误信息
            if '404' in error_msg:
                return {
                    'success': False,
                    'error': f'仓库不存在或无权访问: {repo_url}\n请检查:\n1. 仓库名是否正确\n2. 仓库是否为私有（需要相应权限）\n3. 仓库是否已被删除或重命名'
                }
            elif '403' in error_msg:
                return {
                    'success': False,
                    'error': f'访问被拒绝: {repo_url}\n可能原因:\n1. API 请求限制已达上限\n2. Token 权限不足\n3. 仓库为私有且无访问权限'
                }
            elif '401' in error_msg:
                return {
                    'success': False,
                    'error': f'认证失败: GitHub Token 可能无效或已过期\n请检查 .env 文件中的 GITHUB_TOKEN 设置'
                }
            else:
                return {
                    'success': False,
                    'error': f'获取仓库信息失败: {error_msg}'
                }
        
    
    def get_issues(self, repo_full_name, state='all', page=1, per_page=20):
        """获取仓库的 Issues"""
        try:
            repo = self.github.get_repo(repo_full_name)
            issues = repo.get_issues(state=state, sort='updated', direction='desc')
            
            # 分页处理
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            issues_list = []
            for i, issue in enumerate(issues):
                if i < start_idx:
                    continue
                if i >= end_idx:
                    break
                
                # 跳过 Pull Requests
                if issue.pull_request:
                    continue
                
                issues_list.append({
                    'number': issue.number,
                    'title': issue.title,
                    'body': issue.body,
                    'state': issue.state,
                    'user': {
                        'login': issue.user.login,
                        'avatar_url': issue.user.avatar_url
                    },
                    'labels': [{'name': label.name, 'color': label.color} for label in issue.labels],
                    'created_at': issue.created_at.isoformat(),
                    'updated_at': issue.updated_at.isoformat(),
                    'comments_count': issue.comments,
                    'html_url': issue.html_url
                })
            
            return {
                'success': True,
                'data': issues_list,
                'total_count': repo.open_issues_count
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_issue(self, repo_full_name, issue_number, body):
        """更新 Issue 内容"""
        try:
            repo = self.github.get_repo(repo_full_name)
            issue = repo.get_issue(issue_number)
            issue.edit(body=body)
            
            return {
                'success': True,
                'message': 'Issue 更新成功'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'更新 Issue 失败: {str(e)}'
            }
    
    def create_comment(self, repo_full_name, issue_number, body):
        """创建新评论"""
        try:
            repo = self.github.get_repo(repo_full_name)
            issue = repo.get_issue(issue_number)
            comment = issue.create_comment(body)
            
            return {
                'success': True,
                'message': '评论创建成功',
                'data': {
                    'id': comment.id,
                    'body': comment.body,
                    'user': {
                        'login': comment.user.login,
                        'avatar_url': comment.user.avatar_url
                    },
                    'created_at': comment.created_at.isoformat(),
                    'updated_at': comment.updated_at.isoformat()
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'创建评论失败: {str(e)}'
            }
    
    def update_comment(self, repo_full_name, comment_id, body):
        """更新评论内容"""
        try:
            # 直接通过GitHub实例获取评论
            comment = self.github.get_repo(repo_full_name).get_issue_comment(comment_id)
            comment.edit(body)
            
            return {
                'success': True,
                'message': '评论更新成功'
            }
        except Exception as e:
            # 如果上面的方法不行，尝试使用requests直接调用API
            try:
                url = f'https://api.github.com/repos/{repo_full_name}/issues/comments/{comment_id}'
                response = self.session.patch(url, json={'body': body})
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'message': '评论更新成功'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'更新评论失败: HTTP {response.status_code}'
                    }
            except Exception as e2:
                return {
                    'success': False,
                    'error': f'更新评论失败: {str(e2)}'
                }
    
    def delete_comment(self, repo_full_name, comment_id):
        """删除评论"""
        try:
            # 直接通过GitHub实例获取评论并删除
            comment = self.github.get_repo(repo_full_name).get_issue_comment(comment_id)
            comment.delete()
            
            return {
                'success': True,
                'message': '评论删除成功'
            }
        except Exception as e:
            # 如果上面的方法不行，尝试使用requests直接调用API
            try:
                url = f'https://api.github.com/repos/{repo_full_name}/issues/comments/{comment_id}'
                response = self.session.delete(url)
                
                if response.status_code == 204:
                    return {
                        'success': True,
                        'message': '评论删除成功'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'删除评论失败: HTTP {response.status_code}'
                    }
            except Exception as e2:
                return {
                    'success': False,
                    'error': f'删除评论失败: {str(e2)}'
                }
    
    def get_issue_comments(self, repo_full_name, issue_number):
        """获取 Issue 的所有评论"""
        try:
            repo = self.github.get_repo(repo_full_name)
            issue = repo.get_issue(issue_number)
            comments = issue.get_comments()
            
            comments_list = []
            for comment in comments:
                comments_list.append({
                    'id': comment.id,
                    'body': comment.body,
                    'user': {
                        'login': comment.user.login,
                        'avatar_url': comment.user.avatar_url
                    },
                    'created_at': comment.created_at.isoformat(),
                    'updated_at': comment.updated_at.isoformat(),
                    'html_url': comment.html_url
                })
            
            return {
                'success': True,
                'data': comments_list
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_issue_detail(self, repo_full_name, issue_number):
        """获取 Issue 详细信息"""
        try:
            repo = self.github.get_repo(repo_full_name)
            issue = repo.get_issue(issue_number)
            
            return {
                'success': True,
                'data': {
                    'number': issue.number,
                    'title': issue.title,
                    'body': issue.body,
                    'state': issue.state,
                    'user': {
                        'login': issue.user.login,
                        'avatar_url': issue.user.avatar_url
                    },
                    'labels': [{'name': label.name, 'color': label.color} for label in issue.labels],
                    'milestone': issue.milestone.title if issue.milestone else None,
                    'assignees': [{'login': assignee.login, 'avatar_url': assignee.avatar_url} for assignee in issue.assignees],
                    'created_at': issue.created_at.isoformat(),
                    'updated_at': issue.updated_at.isoformat(),
                    'comments_count': issue.comments,
                    'html_url': issue.html_url
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }