# Vercel 部署指南

## 🚀 快速开始

### 方式一：GitHub 自动部署（推荐）⭐

这是最简单且最推荐的方式，适合持续开发：

#### 步骤：

1. **访问 Vercel Dashboard**
   - 打开 [https://vercel.com](https://vercel.com)
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "Add New" → "Project"
   - 选择 "Import Git Repository"
   - 找到并选择 `anzchy/hubnote-vercel` 仓库
   - 点击 "Import"

3. **配置项目**
   - **Framework Preset**: 选择 "Other" 或 "Python"
   - **Root Directory**: 保持默认（根目录）
   - **Build Command**: 留空（Vercel 会自动识别 `vercel.json`）
   - **Output Directory**: 留空

4. **设置环境变量** ⚠️ 必须设置
   
   在 "Environment Variables" 部分添加以下变量：
   
   ```bash
   # 必需
   SECRET_KEY=<生成一个随机密钥>
   
   # 存储配置（必需）
   STORAGE_TYPE=vercel_blob
   BLOB_READ_WRITE_TOKEN=<从 Vercel Storage 获取>
   
   # 可选但推荐
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```
   
   **生成 SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   
   **获取 BLOB_READ_WRITE_TOKEN**:
   - 在 Vercel 项目设置中
   - 进入 "Storage" → "Blob" 
   - 点击 "Create Storage"
   - 复制生成的 Token

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约 1-2 分钟）
   - 获得部署 URL，例如: `https://your-project.vercel.app`

6. **自动部署配置**
   - 每次 push 到 `main` 分支会自动触发部署
   - Pull Request 会创建预览部署
   - 可以在 Vercel Dashboard 查看部署日志

---

### 方式二：CLI 手动部署

适合临时部署或测试：

#### 前提条件

1. 已安装 Node.js 和 npm
2. 项目中已安装 Vercel CLI（已完成）

#### 步骤：

##### 1. 获取 Vercel Token

访问 [Vercel Account Tokens](https://vercel.com/account/tokens)，创建新 Token：
- Token Name: `hubnote-cli`
- Scope: 选择你的账号/团队
- Expiration: 选择过期时间
- 点击 "Create" 并保存 Token

##### 2. 设置 Token（三种方式）

**方式 A: 环境变量**
```bash
export VERCEL_TOKEN=your_token_here
```

**方式 B: 使用脚本参数**
```bash
./deploy-vercel.sh --token your_token_here --prod
```

**方式 C: 交互式登录**
```bash
npx vercel login
```

##### 3. 部署到生产环境

```bash
# 使用部署脚本（推荐）
./deploy-vercel.sh --prod

# 或直接使用 vercel CLI
npx vercel --prod
```

##### 4. 部署到预览环境

```bash
# 创建预览部署
npx vercel

# 或使用脚本
./deploy-vercel.sh
```

---

## 📊 常用命令

### 查看部署状态
```bash
npx vercel ls
```

### 查看项目信息
```bash
npx vercel inspect [deployment-url]
```

### 查看部署日志
```bash
npx vercel logs [deployment-url]
```

### 查看环境变量
```bash
npx vercel env ls
```

### 添加环境变量
```bash
npx vercel env add SECRET_KEY
# 然后输入值
```

### 删除部署
```bash
npx vercel rm [deployment-url]
```

---

## 🔧 环境变量配置

### 必需的环境变量

| 变量名 | 说明 | 示例 | 获取方式 |
|--------|------|------|----------|
| `SECRET_KEY` | Flask 密钥 | `abc123...` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `STORAGE_TYPE` | 存储类型 | `vercel_blob` | 固定值 |
| `BLOB_READ_WRITE_TOKEN` | Blob 存储 Token | `vercel_blob_...` | Vercel Storage 面板 |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | Flask 环境 | `production` |
| `FLASK_DEBUG` | 调试模式 | `False` |
| `KV_REST_API_URL` | KV 存储 URL | - |
| `KV_REST_API_TOKEN` | KV 存储 Token | - |

---

## 🔍 故障排查

### 部署失败

1. **检查构建日志**
   ```bash
   npx vercel logs [deployment-url]
   ```

2. **验证环境变量**
   ```bash
   npx vercel env ls
   ```

3. **本地测试**
   ```bash
   cd /home/user/webapp
   python api/index.py
   ```

### 常见错误

#### Error: No existing credentials found
```bash
# 解决方案 1: 登录
npx vercel login

# 解决方案 2: 使用 Token
export VERCEL_TOKEN=your_token_here
npx vercel --prod
```

#### Error: Missing environment variables
```bash
# 在 Vercel Dashboard 中添加环境变量
# Settings → Environment Variables
```

#### Error: Build failed
```bash
# 检查 vercel.json 配置
cat vercel.json

# 检查 Python 依赖
cat requirements.txt
```

---

## 📚 部署后检查清单

- [ ] 访问部署的 URL，验证网站可以打开
- [ ] 测试登录功能
- [ ] 测试添加仓库功能
- [ ] 检查 Issues 列表显示
- [ ] 验证评论功能
- [ ] 检查用户管理（如果是管理员）
- [ ] 查看 Vercel 日志，确认没有错误

---

## 🎯 最佳实践

1. **使用 GitHub 自动部署**
   - 代码推送自动部署
   - 有完整的部署历史
   - 支持回滚

2. **环境变量管理**
   - 敏感信息使用环境变量
   - 不要将 Token 提交到代码库
   - 生产和预览环境使用不同的变量

3. **部署前检查**
   - 运行测试
   - 本地验证功能
   - 检查环境变量配置

4. **监控和日志**
   - 定期查看 Vercel 日志
   - 设置错误告警
   - 监控性能指标

---

## 🔗 相关链接

- [Vercel Dashboard](https://vercel.com)
- [Vercel CLI 文档](https://vercel.com/docs/cli)
- [Vercel Python 运行时](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Vercel Storage 文档](https://vercel.com/docs/storage)
- [项目 GitHub 仓库](https://github.com/anzchy/hubnote-vercel)

---

## 💡 提示

- 首次部署后，Vercel 会自动创建 `.vercel` 目录（已添加到 `.gitignore`）
- 生产部署 URL 格式: `https://project-name.vercel.app`
- 预览部署 URL 格式: `https://project-name-git-branch.vercel.app`
- 可以在 Vercel Dashboard 绑定自定义域名
