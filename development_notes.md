# HubNote 开发笔记

## 项目概述
HubNote 是一个基于 Flask 的 GitHub Issues 管理工具，支持查看、管理和导出 GitHub 仓库的 Issues。

## 开发历程

### 端口配置修改
- **问题**：应用默认端口 5000 与其他服务冲突
- **解决方案**：
  - 修改 `run.py`：开发模式端口改为 8888，打包模式端口改为 8889
  - 修改 `app.py`：开发模式端口改为 8888
- **文件修改**：
  - `run.py`: 第 20-21 行端口配置
  - `app.py`: 第 382 行端口配置

### 静态网站生成

#### 问题排查
1. **frozen_flask 模块导入错误**
   - 错误：`ModuleNotFoundError: No module named 'frozen_flask'`
   - 原因：包名引用错误
   - 解决：正确导入方式为 `from flask_frozen import Freezer`

2. **Frozen-Flask 路由冲突**
   - 错误：`ValueError: Unexpected status '405 METHOD NOT ALLOWED' on URL /add_repo`
   - 原因：Frozen-Flask 自动发现所有路由，包括 POST 路由
   - 解决：采用手动生成静态文件的方式

#### 最终解决方案
创建 `freeze.py` 文件，使用手动方式生成静态网站：
- 只生成配置页面 (`/config`)
- 手动复制静态资源
- 创建首页重定向文件
- 生成 CNAME 文件用于自定义域名

#### 生成的文件结构
```
build/
├── index.html      # 首页重定向
├── config.html     # 配置页面
├── CNAME          # 自定义域名配置
└── static/        # 静态资源
    ├── css/
    ├── js/
    └── images/
```

### 部署方案讨论

#### 1. GitHub Pages 部署（静态）
- **适用场景**：展示和演示
- **限制**：无法提供动态功能（GitHub API 交互、数据存储等）
- **步骤**：
  1. 运行 `python freeze.py` 生成静态文件
  2. 将 `build/` 目录内容推送到 GitHub Pages 仓库
  3. 配置自定义域名 `note.jackcheng.chat`

#### 2. 服务器端部署（动态）
推荐平台：
- **Heroku**：适合个人项目，部署简单
- **Railway**：现代化界面，GitHub 集成
- **DigitalOcean App Platform**：生产环境推荐
- **Vercel**：支持 Python，全球 CDN

#### 3. Vercel 部署详细方案
**配置文件**：
- `vercel.json`：Vercel 部署配置
- 修改 `app.py` 添加 Vercel 入口点

**部署步骤**：
1. 安装 Vercel CLI
2. 创建配置文件
3. 设置环境变量
4. 执行部署命令
5. 配置自定义域名

## 技术要点

### Flask 应用结构
```
HubNote-app/
├── app.py              # 主应用文件
├── run.py              # 启动脚本
├── config.py           # 配置文件
├── requirements.txt    # 依赖列表
├── api/               # GitHub API 服务
├── static/            # 静态资源
├── templates/         # HTML 模板
└── utils/             # 工具模块
```

### 关键功能
- GitHub Token 验证和配置
- 仓库 Issues 获取和展示
- Issue 详情查看和评论管理
- 数据导出功能（JSON/CSV）
- Markdown 渲染支持

### 环境配置
- Python 3.9+
- Flask 2.3.3
- flask-cors 4.0.0
- requests 2.31.0
- Conda 环境：`hubnote-env`

## 部署选择建议

### 静态部署（GitHub Pages）
- **优势**：免费、简单、快速
- **劣势**：功能受限，无法进行 GitHub API 交互
- **适用**：项目展示、文档说明

### 动态部署（云平台）
- **优势**：完整功能、可扩展、专业
- **劣势**：需要费用、配置复杂
- **适用**：生产使用、完整体验

## 域名配置
目标域名：`note.jackcheng.chat`
- GitHub Pages：CNAME 记录指向 `<username>.github.io`
- 云平台：根据平台要求配置 CNAME 或 A 记录

## 后续优化方向
1. 添加用户认证系统
2. 支持多用户数据隔离
3. 增加更多 GitHub API 功能
4. 优化前端用户体验
5. 添加数据缓存机制

---

*最后更新：2024年12月*