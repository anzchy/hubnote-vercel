import os
import json
from typing import Dict, Any, Optional
import requests
# 不再依赖 vercel_blob SDK，直接使用 REST API
VERCEL_BLOB_AVAILABLE = True

class StorageManager:
    """存储管理器，支持 Vercel KV 和降级存储方案"""
    
    def __init__(self):
        # 获取存储类型
        self.storage_type = os.getenv('STORAGE_TYPE', 'memory')
        
        # 在开发环境中默认使用文件存储
        if os.getenv('FLASK_ENV') == 'development' or os.getenv('FLASK_DEBUG') == 'true':
            self.storage_type = 'file'
            
        self.kv_url = os.getenv('KV_REST_API_URL')
        self.kv_token = os.getenv('KV_REST_API_TOKEN')
        self.blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
        
        # 检测 Vercel 环境
        self.is_vercel = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None
        
        # Vercel 环境自动选择合适的存储
        if self.is_vercel:
            if self.kv_url and self.kv_token:
                self.storage_type = 'vercel_kv'
                print("🔧 检测到 Vercel 环境，自动切换到 Vercel KV 存储")
            elif self.blob_token:
                self.storage_type = 'vercel_blob'
                print("🔧 检测到 Vercel 环境，自动切换到 Vercel Blob 存储")
            else:
                self.storage_type = 'memory'
                print("⚠️ 检测到 Vercel 环境，但未配置 KV 或 Blob，使用内存存储（数据不持久化）")
        
        # 调试信息
        print(f"StorageManager 初始化:")
        print(f"  - 运行环境: {'Vercel' if self.is_vercel else '本地/其他'}")
        print(f"  - 存储类型: {self.storage_type}")
        print(f"  - KV URL: {self.kv_url or '未设置'}")
        print(f"  - KV Token: {'已设置' if self.kv_token else '未设置'}")
        print(f"  - Blob Token: {'已设置' if self.blob_token else '未设置'}")
        
        # 内存存储（Vercel 环境下的临时方案）
        self._memory_storage = {}
        
        # 降级存储的默认数据
        self._fallback_data = {
            'repositories': [],
            'user_preferences': {},
            'cache': {}
        }
    
    def get_repos(self, force_refresh: bool = False) -> Dict[str, Any]:
        """获取仓库列表"""
        try:
            print(f"📥 获取仓库数据: 存储类型={self.storage_type}, 强制刷新={force_refresh}")
            
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                print("📥 使用 Vercel KV 存储读取数据")
                result = self._get_from_kv('repos')
                return result if result is not None else self._fallback_data
            elif self.storage_type == 'vercel_blob' and self.blob_token:
                print("📥 使用 Vercel Blob 存储读取数据")
                if force_refresh:
                    print("🔄 强制刷新：清除内存缓存并重新从 Blob 读取")
                    # 清除可能的内存缓存
                    if hasattr(self, '_memory_storage'):
                        self._memory_storage.pop('repos', None)
                return self._get_from_blob('repos')
            elif self.storage_type == 'memory':
                print("📥 使用内存存储读取数据")
                return self._get_from_memory('repos')
            elif self.is_vercel:
                # Vercel 环境下不能使用文件存储
                print(f"⚠️ Vercel 环境不支持文件存储，使用内存存储")
                return self._get_from_memory('repos')
            else:
                print("📥 使用文件存储读取数据")
                return self._get_from_file('repos')
        except Exception as e:
            print(f"❌ 获取仓库数据失败: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_data
    
    def get_user_repos(self, username: str, is_admin: bool = False) -> Dict[str, Any]:
        """根据用户权限获取仓库列表"""
        try:
            print(f"获取用户仓库: username={username}, is_admin={is_admin}")
            
            # 非管理员用户强制刷新，解决 Blob 最终一致性问题
            force_refresh = not is_admin
            all_repos = self.get_repos(force_refresh=force_refresh)
            print(f"所有仓库数量: {len(all_repos.get('repositories', []))}")
            
            # 如果是管理员，返回所有仓库
            if is_admin:
                print("用户是管理员，返回所有仓库")
                return all_repos
            
            # 如果是普通用户，处理仓库权限
            user_repos = {
                'repositories': [],
                'total_count': 0,
                'last_updated': all_repos.get('last_updated', '')
            }
            
            repositories = all_repos.get('repositories', [])
            print(f"所有仓库列表: {[repo.get('full_name') for repo in repositories]}")
            
            # 混合权限控制：优先使用added_by字段，回退到owner字段
            print("使用混合权限控制策略")
            for repo in repositories:
                repo_added_by = repo.get('added_by', '')
                repo_owner = repo.get('owner', '')
                
                print(f"仓库 {repo.get('full_name')}: added_by='{repo_added_by}', owner='{repo_owner}', 当前用户='{username}'")
                
                # 策略1：如果仓库有added_by字段，按added_by过滤
                if repo_added_by and repo_added_by == username:
                    user_repos['repositories'].append(repo)
                    print(f"✅ 用户 {username} 可见仓库（added_by匹配）: {repo.get('full_name')}")
                    continue
                
                # 策略2：如果仓库没有added_by字段，按owner过滤（向后兼容）
                if not repo_added_by and repo_owner.lower() == username.lower():
                    user_repos['repositories'].append(repo)
                    print(f"✅ 用户 {username} 可见仓库（owner匹配）: {repo.get('full_name')}")
                    continue
                
                print(f"❌ 用户 {username} 无权访问仓库: {repo.get('full_name')}")
            
            user_repos['total_count'] = len(user_repos['repositories'])
            print(f"用户 {username} 可见仓库数量: {user_repos['total_count']}")
            print(f"可见仓库列表: {[repo.get('full_name') for repo in user_repos['repositories']]}")
            
            return user_repos
            
        except Exception as e:
            print(f"获取用户仓库失败: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_data
    
    def save_repos(self, data: Dict[str, Any]) -> bool:
        """保存仓库列表"""
        try:
            print(f"💾 开始保存仓库数据 (存储类型: {self.storage_type})")
            
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                print(f"📤 使用 Vercel KV 保存数据")
                return self._save_to_kv('repos', data)
            elif self.storage_type == 'vercel_blob' and self.blob_token:
                print(f"📤 使用 Vercel Blob 保存数据")
                return self._save_to_blob('repos', data)
            elif self.storage_type == 'memory':
                print(f"📤 使用内存保存数据 (⚠️ 数据不持久化)")
                return self._save_to_memory('repos', data)
            elif self.is_vercel:
                # Vercel 环境下不能使用文件存储
                print(f"❌ Vercel 环境不支持文件存储，请配置 KV_REST_API_URL 和 KV_REST_API_TOKEN")
                print(f"⚠️ 降级到内存存储，数据将在重启后丢失")
                return self._save_to_memory('repos', data)
            else:
                print(f"📤 使用文件存储保存数据")
                return self._save_to_file('repos', data)
        except Exception as e:
            print(f"❌ 保存仓库数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好设置"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._get_from_kv(f'user_prefs_{user_id}')
            else:
                return self._get_from_env(f'USER_PREFS_{user_id}')
        except Exception as e:
            print(f"获取用户偏好失败: {e}")
            return {}
    
    def save_user_preferences(self, user_id: str, data: Dict[str, Any]) -> bool:
        """保存用户偏好设置"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._save_to_kv(f'user_prefs_{user_id}', data)
            else:
                print("警告: 当前存储方案不支持写入操作")
                return False
        except Exception as e:
            print(f"保存用户偏好失败: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._get_from_kv(f'cache_{key}')
            else:
                return None
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
    
    def set_cache(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """设置缓存数据"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                cache_data = {
                    'data': data,
                    'expires_at': self._get_expiry_time(ttl)
                }
                return self._save_to_kv(f'cache_{key}', cache_data)
            else:
                return False
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    def get_user_whitelist(self) -> Dict[str, Any]:
        """获取用户白名单"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._get_from_kv('user_whitelist')
            elif self.storage_type == 'memory':
                return self._get_from_memory('user_whitelist')
            else:
                return self._get_from_file('user_whitelist')
        except Exception as e:
            print(f"获取用户白名单失败: {e}")
            return {'allowed_users': [], 'admin_users': []}
    
    def save_user_whitelist(self, data: Dict[str, Any]) -> bool:
        """保存用户白名单"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._save_to_kv('user_whitelist', data)
            elif self.storage_type == 'memory':
                return self._save_to_memory('user_whitelist', data)
            else:
                return self._save_to_file('user_whitelist', data)
        except Exception as e:
            print(f"保存用户白名单失败: {e}")
            return False
    
    def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._get_from_kv('user_stats')
            elif self.storage_type == 'memory':
                return self._get_from_memory('user_stats')
            else:
                return self._get_from_file('user_stats')
        except Exception as e:
            print(f"获取用户统计信息失败: {e}")
            return {}
    
    def save_user_stats(self, data: Dict[str, Any]) -> bool:
        """保存用户统计信息"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._save_to_kv('user_stats', data)
            elif self.storage_type == 'memory':
                return self._save_to_memory('user_stats', data)
            else:
                return self._save_to_file('user_stats', data)
        except Exception as e:
            print(f"保存用户统计信息失败: {e}")
            return False
    
    def record_user_login(self, username: str) -> bool:
        """记录用户登录"""
        try:
            stats = self.get_user_stats()
            
            # 获取当前时间
            import datetime
            now = datetime.datetime.now()
            today = now.strftime('%Y-%m-%d')
            
            # 初始化用户统计
            if 'user_stats' not in stats:
                stats['user_stats'] = {}
            if 'daily_stats' not in stats:
                stats['daily_stats'] = {}
            if 'total_logins' not in stats:
                stats['total_logins'] = 0
            
            # 更新用户统计
            if username not in stats['user_stats']:
                stats['user_stats'][username] = {
                    'login_count': 0,
                    'last_login': None,
                    'first_login': None
                }
            
            user_stat = stats['user_stats'][username]
            user_stat['login_count'] += 1
            user_stat['last_login'] = now.isoformat()
            if not user_stat['first_login']:
                user_stat['first_login'] = now.isoformat()
            
            # 更新总体统计
            stats['total_logins'] += 1
            
            # 更新今日统计
            if today not in stats['daily_stats']:
                stats['daily_stats'][today] = {'logins': 0}
            stats['daily_stats'][today]['logins'] += 1
            
            return self.save_user_stats(stats)
            
        except Exception as e:
            print(f"记录用户登录失败: {e}")
            return False
    
    def _get_from_kv(self, key: str) -> Any:
        """从 Vercel KV 获取数据"""
        if not self.kv_url or not self.kv_token:
            raise Exception("Vercel KV 配置不完整")
        
        headers = {
            'Authorization': f'Bearer {self.kv_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{self.kv_url}/get/{key}", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('result'):
                return json.loads(result['result'])
            return None
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"KV 读取失败: HTTP {response.status_code}")
    
    def _save_to_kv(self, key: str, data: Any) -> bool:
        """保存数据到 Vercel KV"""
        if not self.kv_url or not self.kv_token:
            raise Exception("Vercel KV 配置不完整")
        
        headers = {
            'Authorization': f'Bearer {self.kv_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'value': json.dumps(data, ensure_ascii=False)
        }
        
        response = requests.post(f"{self.kv_url}/set/{key}", 
                               headers=headers, 
                               json=payload)
        
        return response.status_code == 200
    
    def _get_from_env(self, key: str) -> Any:
        """从环境变量获取数据（降级方案）"""
        data_str = os.getenv(key, '{}')
        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            return {}
    
    def _get_expiry_time(self, ttl: int) -> int:
        """获取过期时间戳"""
        import time
        return int(time.time()) + ttl
    
    def clear_expired_cache(self) -> bool:
        """清理过期的缓存数据"""
        try:
            if self.storage_type != 'vercel_kv':
                return False
            
            # 获取所有缓存键
            # 这里需要实现获取所有键的逻辑
            # 由于 Vercel KV 的限制，可能需要手动管理缓存键
            return True
        except Exception as e:
            print(f"清理缓存失败: {e}")
            return False
    
    def _get_from_file(self, key: str) -> Any:
        """从本地文件获取数据（降级方案）"""
        try:
            # 创建数据目录
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            file_path = os.path.join(data_dir, f'{key}.json')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._fallback_data if key == 'repos' else {}
        except Exception as e:
            print(f"从文件读取数据失败: {e}")
            return self._fallback_data if key == 'repos' else {}
    
    def _save_to_file(self, key: str, data: Any) -> bool:
        """保存数据到本地文件（降级方案）"""
        try:
            # 创建数据目录
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            file_path = os.path.join(data_dir, f'{key}.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存数据到文件失败: {e}")
            return False
    
    def _get_from_memory(self, key: str) -> Any:
        """从内存获取数据"""
        return self._memory_storage.get(key, self._fallback_data if key == 'repos' else {})
    
    def _save_to_memory(self, key: str, data: Any) -> bool:
        """保存数据到内存"""
        try:
            self._memory_storage[key] = data
            return True
        except Exception as e:
            print(f"保存数据到内存失败: {e}")
            return False
    
    def _get_from_blob(self, key: str) -> Any:
        """从 Vercel Blob 获取数据"""
        if not self.blob_token:
            print("Vercel Blob token 未配置，使用降级存储")
            return self._get_from_memory(key)
        
        max_retries = 10  # 增加重试次数
        retry_delay = 2.0  # 从2秒开始
        
        for attempt in range(max_retries):
            try:
                # 使用 Vercel Blob REST API 获取文件列表
                headers = {
                    'Authorization': f'Bearer {self.blob_token}'
                }
                
                list_url = 'https://blob.vercel-storage.com/'
                response = requests.get(list_url, headers=headers)
                
                if response.status_code == 200:
                    blobs_data = response.json()
                    target_filename = f"{key}.json"
                    
                    # 查找对应的文件
                    for blob in blobs_data.get('blobs', []):
                        if blob.get('pathname') == target_filename:
                            # 下载并解析 JSON 数据
                            file_response = requests.get(blob['url'])
                            if file_response.status_code == 200:
                                data = file_response.json()
                                repo_count = len(data.get('repositories', []))
                                print(f"Blob 读取成功 (尝试 {attempt + 1}/{max_retries}): {repo_count} 个仓库")
                                
                                # 如果是第一次读取，记录仓库列表用于调试
                                if attempt == 0:
                                    repo_names = [repo.get('full_name') for repo in data.get('repositories', [])]
                                    print(f"当前仓库列表: {repo_names}")
                                
                                return data
                
                # 如果没找到文件，返回默认数据
                if attempt == max_retries - 1:
                    print(f"Blob 读取失败，已达到最大重试次数")
                    return self._fallback_data if key == 'repos' else {}
                
                print(f"Blob 读取失败，等待 {retry_delay}s 后重试 (尝试 {attempt + 1}/{max_retries})")
                import time
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 30.0)  # 更温和的指数退避，最大30秒
                
            except Exception as e:
                print(f"从 Blob 读取数据失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return self._fallback_data if key == 'repos' else {}
                import time
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 30.0)
    
    def _save_to_blob(self, key: str, data: Any) -> bool:
        """保存数据到 Vercel Blob"""
        if not self.blob_token:
            print("Vercel Blob token 未配置，使用降级存储")
            return self._save_to_memory(key, data)
        
        try:
            # 将数据转换为 JSON 字符串
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 使用 Vercel Blob REST API 上传文件
            headers = {
                'Authorization': f'Bearer {self.blob_token}',
                'Content-Type': 'application/json'
            }
            
            filename = f"{key}.json"
            upload_url = f'https://blob.vercel-storage.com/{filename}'
            
            response = requests.put(
                upload_url,
                headers=headers,
                data=json_data.encode('utf-8')
            )
            
            if response.status_code in [200, 201]:
                print(f"数据成功保存到 Blob: {filename}")
                return True
            else:
                print(f"保存到 Blob 失败: HTTP {response.status_code}")
                return False
            
        except Exception as e:
            print(f"保存数据到 Blob 失败: {e}")
            return False
