# HubNote

一个简洁的 GitHub Issues 管理工具，帮助你更好地跟踪和管理多个仓库的 Issues。现已支持打包为独立的 macOS 应用程序！

## 功能特性

- 📚 **多仓库管理**: 添加和管理多个 GitHub 仓库
- 🔍 **Issues 浏览**: 查看仓库的所有 Issues，支持筛选和搜索
- 💬 **评论查看**: 查看 Issue 的详细内容和所有评论
- 🏷️ **标签支持**: 显示 Issue 标签，支持按标签筛选
- 📊 **统计信息**: 显示仓库和 Issues 的统计数据
- 🎨 **现代界面**: 简洁美观的用户界面
- 📱 **响应式设计**: 支持桌面和移动设备

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd hubnote
```

### 2. 创建和激活虚拟环境

**方法一：使用提供的激活脚本（推荐）**

```bash
# 创建虚拟环境（仅首次需要）
python3 -m venv gitnote-venv

# 使用激活脚本
source activate_env.sh
```

**方法二：手动操作**

```bash
# 创建虚拟环境
python3 -m venv gitnote-venv

# 激活虚拟环境
source hubnote-venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**注意**: 在 macOS 上，由于 PEP 668 的限制，必须使用虚拟环境来安装 Python 包。

## 📱 应用打包

HubNote 支持打包为独立的 macOS 应用程序，用户无需安装 Python 环境即可使用。

### 快速打包

```bash
# 一键打包（推荐）
./build_app.sh
```

### 手动打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 执行打包
pyinstaller HubNote.spec
```

### 使用打包后的应用

打包完成后，您可以在 `dist/` 目录找到 `HubNote.app`：

- 拖拽到 Applications 文件夹安装
- 或直接双击运行
- 命令行运行：`open dist/HubNote.app`

详细的打包说明请参考 [PACKAGING.md](PACKAGING.md)。

### 3. 配置环境

复制环境配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 GitHub Token：

```env
GITHUB_TOKEN=your_github_token_here
```

### 4. 获取 GitHub Token

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择所需权限：
   - `public_repo`: 访问公开仓库
   - `repo`: 访问私有仓库（如果需要）
4. 复制生成的 token 到 `.env` 文件中

### 5. 运行应用

```bash
python app.py
```

应用将在 http://127.0.0.1:5000 启动。

## 使用说明

### 添加仓库

1. 在主页点击 "添加仓库"
2. 输入 GitHub 仓库 URL 或 `owner/repo` 格式
3. 点击 "添加" 按钮

支持的格式：
- `https://github.com/owner/repo`
- `owner/repo`

### 查看 Issues

1. 在仓库列表中点击 "查看 Issues"
2. 使用筛选器查看不同状态的 Issues
3. 使用搜索框搜索特定的 Issues
4. 点击 Issue 标题查看详细内容

### 查看 Issue 详情

- 查看 Issue 的完整内容
- 浏览所有评论
- 查看 Issue 标签和状态
- 点击链接跳转到 GitHub 原页面

## 项目结构

```
gitnote/
├── app.py                 # Flask 应用主文件
├── config.py              # 配置文件
├── requirements.txt       # Python 依赖
├── .env.example          # 环境配置模板
├── README.md             # 项目说明
├── api/                  # GitHub API 服务
│   ├── __init__.py
│   └── github_service.py
├── utils/                # 工具函数
│   ├── __init__.py
│   └── helpers.py
├── data/                 # 数据存储
│   └── repos.json
├── templates/            # HTML 模板
│   ├── base.html
│   ├── index.html
│   ├── issues.html
│   └── issue_detail.html
└── static/               # 静态资源
    ├── css/
    │   └── main.css
    ├── js/
    │   ├── main.js
    │   ├── repo.js
    │   ├── issues.js
    │   └── comments.js
    └── images/
```

## 技术栈

- **后端**: Python + Flask
- **前端**: HTML + CSS + JavaScript
- **API**: GitHub REST API
- **数据存储**: JSON 文件
- **HTTP 客户端**: requests + PyGithub

## 配置选项

在 `.env` 文件中可以配置以下选项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | 必填 |
| `FLASK_ENV` | Flask 运行环境 | `development` |
| `FLASK_DEBUG` | 是否开启调试模式 | `True` |
| `APP_HOST` | 应用监听地址 | `127.0.0.1` |
| `APP_PORT` | 应用监听端口 | `5000` |
| `CACHE_TIMEOUT` | 缓存超时时间（秒） | `3600` |
| `ISSUES_PER_PAGE` | 每页显示的 Issues 数量 | `30` |

## 故障排除

如果遇到问题（如 GitHub API 404 错误），请参考 [故障排除指南](TROUBLESHOOTING.md)。

### 快速诊断工具

```bash
# 测试 GitHub Token 有效性
python test_github_token.py

# 测试特定仓库访问
python test_repo_access.py owner/repo
```

## 注意事项

1. **API 限制**: GitHub API 对未认证请求有较严格的限制，建议配置 Personal Access Token
2. **Token 权限**: 根据需要访问的仓库类型选择合适的权限
3. **数据存储**: 当前版本使用 JSON 文件存储数据，重启应用不会丢失数据
4. **只读模式**: 当前版本只支持查看功能，不支持创建或修改 Issues
5. **404 错误**: 如遇到 404 错误，请检查仓库名称是否正确且仓库确实存在

## 开发计划

- [ ] 支持 Issue 创建和编辑
- [ ] 添加数据库支持
- [ ] 支持多用户
- [ ] 添加通知功能
- [ ] 支持 Pull Requests
- [ ] 添加数据导出功能

## 贡献

欢迎提交 Issues 和 Pull Requests！

## 许可证

MIT License