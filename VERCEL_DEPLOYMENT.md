# HubNote Vercel 部署指南

本指南介绍如何将 HubNote 部署到 Vercel 平台。

## 🚀 快速部署

### 1. 准备工作

确保你已经：
- 安装了 [Vercel CLI](https://vercel.com/cli)
- 有 GitHub 账号和 Personal Access Token
- 有 Vercel 账号

### 2. 环境变量配置

**重要：** HubNote 在 Vercel 上主要通过环境变量来配置 GitHub Token，这是推荐的安全做法。

在 Vercel 项目设置中配置以下环境变量：

#### 必需的环境变量

```bash
# GitHub API Token (必需)
GITHUB_TOKEN=ghp_your_github_token_here

# Flask 应用密钥 (必需)
SECRET_KEY=your-secret-key-here
```

#### 可选的环境变量

```bash
# Flask 环境配置
FLASK_ENV=production
FLASK_DEBUG=False

# 存储配置
STORAGE_TYPE=vercel_kv

# Vercel KV 配置（如果使用 Vercel KV 存储）
KV_REST_API_URL=https://your-project.vercel-storage.com
KV_REST_API_TOKEN=your_kv_token_here
```

#### 配置步骤：

1. **创建 GitHub Token**：
   - 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - 点击 "Generate new token (classic)"
   - 选择权限：`repo`（完全访问）或 `public_repo`（仅公开仓库）
   - 复制生成的 token

2. **在 Vercel 中配置环境变量**：
   - 在 Vercel 控制台进入您的项目
   - 点击 "Settings" > "Environment Variables"
   - 添加 `GITHUB_TOKEN` = 您的 GitHub token
   - 添加 `SECRET_KEY` = 随机生成的安全密钥

3. **生成安全密钥**：
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### 3. 部署命令

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login

# 部署项目
vercel

# 生产环境部署
vercel --prod
```

## 📁 项目结构

```
hubnote-vercel/
├── api/
│   ├── index.py          # Vercel 主入口点
│   ├── repos.py          # 仓库管理 API
│   ├── issues.py         # Issues 管理 API
│   ├── comments.py       # 评论管理 API
│   └── auth.py           # 认证相关 API
├── services/
│   └── github_service.py # GitHub 服务
├── utils/
│   ├── storage.py        # 存储抽象层
│   ├── auth.py           # 认证工具
│   └── helpers.py        # 辅助函数
├── static/                # 静态文件
├── templates/             # 模板文件
├── vercel.json           # Vercel 配置
└── requirements.txt      # Python 依赖
```

## ⚙️ 配置说明

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

### 存储配置

项目支持两种存储方案：

1. **Vercel KV**（推荐）
   - 高性能键值存储
   - 支持复杂数据结构
   - 自动扩缩容

2. **环境变量**（降级方案）
   - 仅支持只读操作
   - 适合简单配置

## 🔧 功能特性

### 已实现功能

- ✅ 仓库管理（添加/删除/列表）
- ✅ Issues 浏览和详情查看
- ✅ 评论查看和管理
- ✅ 用户认证和权限管理
- ✅ 云端存储支持
- ✅ RESTful API 设计

### 新增功能

- 🆕 Issue 创建和编辑
- 🆕 评论创建和编辑
- 🆕 实时更新支持
- 🆕 用户偏好设置
- 🆕 权限验证系统

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_api.py

# 生成测试报告
python -m pytest --html=report.html
```

### 测试覆盖

- API 端点测试
- 服务层测试
- 工具函数测试
- 集成测试

## 📊 监控和日志

### Vercel 内置功能

- 自动性能监控
- 错误追踪
- 访问日志
- 函数执行统计

### 自定义监控

```python
# 在代码中添加自定义日志
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("API 调用成功")
logger.error("发生错误", exc_info=True)
```

## 🚨 故障排除

### 常见问题

1. **部署失败**
   - 检查 Python 版本兼容性
   - 验证依赖包安装
   - 检查环境变量配置

2. **API 错误**
   - 验证 GitHub Token
   - 检查权限设置
   - 查看 Vercel 函数日志

3. **存储问题**
   - 确认 Vercel KV 配置
   - 检查存储权限
   - 验证数据格式

### 调试技巧

```bash
# 查看 Vercel 函数日志
vercel logs

# 本地测试
vercel dev

# 检查构建状态
vercel ls
```

## 🔄 持续部署

### GitHub 集成

1. 连接 GitHub 仓库
2. 配置自动部署分支
3. 设置环境变量
4. 启用预览部署

### 部署流程

```bash
# 开发分支
git push origin develop
# 自动部署到预览环境

# 主分支
git push origin main
# 自动部署到生产环境
```

## 💰 成本估算

### Vercel 定价

- **Hobby**: $0/月（适合个人项目）
- **Pro**: $20/月（推荐，支持更多功能）
- **Enterprise**: 联系销售

### Vercel KV 定价

- 读取: $0.30/100K 请求
- 写入: $0.60/100K 请求
- 存储: $0.20/GB/月

### 预估月成本

- 小型项目: $5-15/月
- 中型项目: $20-40/月
- 大型项目: $50+/月

## 📚 相关资源

- [Vercel 文档](https://vercel.com/docs)
- [Vercel Python 运行时](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Vercel KV 文档](https://vercel.com/docs/storage/vercel-kv)
- [Flask 部署指南](https://flask.palletsprojects.com/en/2.3.x/deploying/)

## 🤝 支持

如果遇到问题：

1. 查看 Vercel 函数日志
2. 检查环境变量配置
3. 验证 GitHub API 权限
4. 提交 Issue 到项目仓库

---

**注意**: 本指南基于 Vercel 的最新版本编写，如有更新请参考官方文档。
