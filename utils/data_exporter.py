#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出服务
支持将仓库的 Issues 和评论导出为多种格式
"""

import json
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from api.github_service import GitHubService


class DataExporter:
    """数据导出服务类"""
    
    def __init__(self, github_token: Optional[str] = None):
        """初始化导出服务
        
        Args:
            github_token: GitHub API Token
        """
        self.github_service = GitHubService(github_token)
    
    def export_repo_data(self, repo_full_name: str, export_format: str = 'json') -> Dict[str, Any]:
        """导出仓库数据
        
        Args:
            repo_full_name: 仓库全名 (owner/repo)
            export_format: 导出格式 ('json', 'csv')
            
        Returns:
            包含导出数据和元信息的字典
        """
        try:
            # 获取仓库信息
            repo_info_result = self.github_service.get_repo_info(repo_full_name)
            if not repo_info_result.get('success'):
                return {
                    'success': False,
                    'error': repo_info_result.get('error', '获取仓库信息失败')
                }
            
            repo_info = repo_info_result.get('data', {})
            
            # 获取所有 Issues（包括评论）
            issues_data = self._get_all_issues_with_comments(repo_full_name)
            
            # 构建导出数据结构
            export_data = {
                'export_info': {
                    'repo_name': repo_full_name,
                    'repo_description': repo_info.get('description', ''),
                    'export_time': datetime.now().isoformat(),
                    'total_issues': len(issues_data),
                    'total_comments': sum(len(issue.get('comments', [])) for issue in issues_data),
                    'export_format': export_format
                },
                'repository': {
                    'name': repo_info.get('name', ''),
                    'full_name': repo_full_name,
                    'description': repo_info.get('description', ''),
                    'url': repo_info.get('url', ''),
                    'stars': repo_info.get('stars', 0),
                    'forks': repo_info.get('forks', 0),
                    'language': repo_info.get('language', ''),
                    'open_issues': repo_info.get('open_issues', 0)
                },
                'issues': issues_data
            }
            
            # 根据格式生成导出内容
            if export_format.lower() == 'json':
                content, filename = self._export_json(export_data, repo_full_name)
            elif export_format.lower() == 'csv':
                content, filename = self._export_csv(export_data, repo_full_name)
            else:
                return {
                    'success': False,
                    'error': f'不支持的导出格式: {export_format}'
                }
            
            return {
                'success': True,
                'content': content,
                'filename': filename,
                'content_type': self._get_content_type(export_format),
                'export_info': export_data['export_info']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'导出数据时发生错误: {str(e)}'
            }
    
    def _get_all_issues_with_comments(self, repo_full_name: str) -> List[Dict[str, Any]]:
        """获取所有 Issues 及其评论
        
        Args:
            repo_full_name: 仓库全名
            
        Returns:
            包含 Issues 和评论的列表
        """
        all_issues = []
        page = 1
        per_page = 100  # GitHub API 最大值
        
        while True:
            # 获取 Issues
            issues_result = self.github_service.get_issues(
                repo_full_name, 
                state='all', 
                page=page, 
                per_page=per_page
            )
            
            if not issues_result.get('success'):
                break
                
            issues = issues_result.get('data', [])
            if not issues:
                break
            
            # 为每个 Issue 获取评论
            for issue in issues:
                issue_number = issue.get('number')
                if issue_number:
                    comments_result = self.github_service.get_issue_comments(
                        repo_full_name, 
                        issue_number
                    )
                    
                    if comments_result.get('success'):
                        issue['comments'] = comments_result.get('data', [])
                    else:
                        issue['comments'] = []
                
                all_issues.append(issue)
            
            # 如果返回的 Issues 数量少于请求数量，说明已经是最后一页
            if len(issues) < per_page:
                break
                
            page += 1
        
        return all_issues
    
    def _export_json(self, data: Dict[str, Any], repo_name: str) -> tuple:
        """导出为 JSON 格式
        
        Args:
            data: 要导出的数据
            repo_name: 仓库名称
            
        Returns:
            (content, filename) 元组
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{repo_name.replace('/', '_')}_export_{timestamp}.json"
        
        content = json.dumps(data, ensure_ascii=False, indent=2)
        
        return content, filename
    
    def _export_csv(self, data: Dict[str, Any], repo_name: str) -> tuple:
        """导出为 CSV 格式
        
        Args:
            data: 要导出的数据
            repo_name: 仓库名称
            
        Returns:
            (content, filename) 元组
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{repo_name.replace('/', '_')}_export_{timestamp}.csv"
        
        # 创建 CSV 内容
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = [
            'Issue Number', 'Title', 'State', 'Author', 'Created At', 'Updated At',
            'Labels', 'Body', 'Comments Count', 'Comment ID', 'Comment Author', 
            'Comment Created At', 'Comment Body'
        ]
        writer.writerow(headers)
        
        # 写入数据
        for issue in data.get('issues', []):
            issue_row = [
                issue.get('number', ''),
                issue.get('title', ''),
                issue.get('state', ''),
                issue.get('author', ''),
                issue.get('created_at', ''),
                issue.get('updated_at', ''),
                ', '.join([label.get('name', '') for label in issue.get('labels', [])]),
                issue.get('body', '').replace('\n', ' ').replace('\r', ' ')[:500],  # 限制长度
                len(issue.get('comments', []))
            ]
            
            comments = issue.get('comments', [])
            if comments:
                # 为每个评论创建一行
                for comment in comments:
                    row = issue_row + [
                        comment.get('id', ''),
                        comment.get('author', ''),
                        comment.get('created_at', ''),
                        comment.get('body', '').replace('\n', ' ').replace('\r', ' ')[:500]
                    ]
                    writer.writerow(row)
            else:
                # 没有评论的 Issue
                row = issue_row + ['', '', '', '']
                writer.writerow(row)
        
        content = output.getvalue()
        output.close()
        
        return content, filename
    
    def _get_content_type(self, export_format: str) -> str:
        """获取内容类型
        
        Args:
            export_format: 导出格式
            
        Returns:
            MIME 类型字符串
        """
        content_types = {
            'json': 'application/json',
            'csv': 'text/csv'
        }
        
        return content_types.get(export_format.lower(), 'application/octet-stream')
    
    def get_available_repos(self) -> List[Dict[str, str]]:
        """获取可用的仓库列表
        
        Returns:
            仓库列表，每个仓库包含 name、full_name、description 和 open_issues
        """
        try:
            from utils.storage import StorageManager
            storage = StorageManager()
            repos_data = storage.get_repos()
            repositories = repos_data.get('repositories', [])
            
            return [{
                'name': repo.get('name', ''),
                'full_name': repo.get('full_name', ''),
                'description': repo.get('description', '')[:100] if repo.get('description') else '暂无描述',
                'open_issues': repo.get('open_issues', 0)
            } for repo in repositories]
            
        except Exception as e:
            print(f"获取仓库列表时发生错误: {e}")
            return []