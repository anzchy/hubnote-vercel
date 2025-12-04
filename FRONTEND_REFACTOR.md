# 前端重构与 Vercel 修复说明

## 1. 问题分析

用户反馈仓库添加成功（日志显示 200 OK），但前端首页不显示仓库列表。
经排查，主要原因如下：
1. **渲染机制问题**：原有的 Jinja2 服务端渲染在 Vercel Serverless 环境下可能存在数据获取时机或缓存问题，导致首次加载时列表为空。
2. **API 完整性问题**：`api/index.py`（Vercel 入口）缺少 `_add_repo` 函数定义，导致手动添加仓库可能失败（尽管用户反馈成功，可能是自动添加逻辑生效）。
3. **样式类名不匹配**：前端使用了 Bootstrap 的 `.spinner-border` 类，但项目中并未引入 Bootstrap，导致加载动画不可见。

## 2. 解决方案

我们实施了前后端分离的渲染重构方案（参考 `github-notebooks`）：

### 2.1 后端 (Python/Flask)
- **新增 API**：在 `app.py` 和 `api/index.py` 中完善了 `/api/my_repos` 接口，返回 JSON 格式的仓库列表。
- **修复逻辑**：在 `api/index.py` 中补全了缺失的 `_add_repo` 函数，确保手动添加仓库功能正常。
- **调整路由**：首页路由 `/` 不再直接传递仓库数据，而是返回空列表，由前端 JS 负责接管数据加载。

### 2.2 前端 (HTML/JS/CSS)
- **HTML (`index.html`)**：
  - 移除了对 Jinja2 `repos` 变量的依赖。
  - 添加了 `loading-state`（加载中）和 `empty-state`（空状态）的占位容器。
  - 确保引入了 `repo.js` 和 `export.js`。
- **JavaScript (`repo.js`)**：
  - 实现了 `loadRepositories()` 函数，页面加载时自动调用 `/api/my_repos`。
  - 增加了数据渲染逻辑：成功获取数据显示网格，无数据/失败显示空状态或错误提示。
  - 完善了添加仓库后的自动刷新逻辑（重新 fetch 而不是 reload 页面）。
- **CSS (`main.css`)**：
  - 新增 `.loading-state` 样式，确保加载提示居中显示。
  - 确认 `.loading-spinner` 样式可用。

## 3. 部署与验证

### 3.1 部署步骤
1. 合并此 PR 到 `main` 分支。
2. 等待 Vercel 自动部署完成。

### 3.2 验证方法
1. 访问首页，应该能看到"正在加载仓库列表..."的提示和旋转动画。
2. 加载完成后，应显示已添加的仓库卡片。
3. 如果列表为空，尝试手动添加 `anzchy/jack-notes`，应提示"仓库已存在"或添加成功并立即显示。
4. 检查浏览器控制台（F12 -> Console），确认 `/api/my_repos` 请求返回 HTTP 200 和正确的 JSON 数据。

## 4. 故障排查
如果仍然不显示：
- 检查 Vercel 环境变量 `STORAGE_TYPE` 是否为 `vercel_kv`。
- 检查 `KV_REST_API_URL` 和 `KV_REST_API_TOKEN` 是否正确配置。
- 尝试清除 Vercel KV 数据（使用 `vercel kv del repos`）并重新登录触发初始化。
