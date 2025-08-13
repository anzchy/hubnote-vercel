import os
import json
from typing import Dict, Any, Optional
import requests
# 不再依赖 vercel_blob SDK，直接使用 REST API
VERCEL_BLOB_AVAILABLE = True

class StorageManager:
    """存储管理器，支持 Vercel KV 和降级存储方案"""
    
    def __init__(self):
        self.storage_type = os.getenv('STORAGE_TYPE', 'memory')
        self.kv_url = os.getenv('KV_REST_API_URL')
        self.kv_token = os.getenv('KV_REST_API_TOKEN')
        self.blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
        
        # 内存存储（Vercel 环境下的临时方案）
        self._memory_storage = {}
        
        # 降级存储的默认数据
        self._fallback_data = {
            'repositories': [],
            'user_preferences': {},
            'cache': {}
        }
    
    def get_repos(self) -> Dict[str, Any]:
        """获取仓库列表"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._get_from_kv('repos')
            elif self.storage_type == 'vercel_blob' and self.blob_token:
                return self._get_from_blob('repos')
            elif self.storage_type == 'memory':
                return self._get_from_memory('repos')
            else:
                return self._get_from_file('repos')
        except Exception as e:
            print(f"获取仓库数据失败: {e}")
            return self._fallback_data
    
    def save_repos(self, data: Dict[str, Any]) -> bool:
        """保存仓库列表"""
        try:
            if self.storage_type == 'vercel_kv' and self.kv_url and self.kv_token:
                return self._save_to_kv('repos', data)
            elif self.storage_type == 'vercel_blob' and self.blob_token:
                return self._save_to_blob('repos', data)
            elif self.storage_type == 'memory':
                return self._save_to_memory('repos', data)
            else:
                return self._save_to_file('repos', data)
        except Exception as e:
            print(f"保存仓库数据失败: {e}")
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
                            return file_response.json()
            
            # 如果没找到文件，返回默认数据
            return self._fallback_data if key == 'repos' else {}
            
        except Exception as e:
            print(f"从 Blob 读取数据失败: {e}")
            return self._fallback_data if key == 'repos' else {}
    
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
