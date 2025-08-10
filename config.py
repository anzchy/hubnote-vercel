import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # GitHub API 配置
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # 应用配置
    REPOS_FILE = 'data/repos.json'
    CACHE_TIMEOUT = 300  # 5分钟缓存
    ISSUES_PER_PAGE = 20
    
    # GitHub API 限制
    API_RATE_LIMIT = 5000  # 每小时请求限制
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}