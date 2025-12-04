# 使用 Vercel CLI 部署示例

## 📋 前提条件

1. ✅ Vercel CLI 已安装（已完成）
2. ⏳ 需要 Vercel Token 或登录凭据

---

## 🔐 方式一：使用 Token 部署

### 1. 获取 Vercel Token

访问：https://vercel.com/account/tokens

创建新 Token：
- Token Name: `hubnote-cli-deploy`
- Scope: 选择你的账号
- Expiration: Never (或选择期限)
- 点击 "Create" 并保存 Token

### 2. 使用 Token 部署

#### 方法 A：设置环境变量
```bash
export VERCEL_TOKEN=your_token_here
cd /home/user/webapp
./deploy-vercel.sh --prod
```

#### 方法 B：直接传递 Token
```bash
cd /home/user/webapp
npx vercel --token your_token_here --prod
```

#### 方法 C：使用脚本参数
```bash
cd /home/user/webapp
./deploy-vercel.sh --token your_token_here --prod
```

---

## 🌐 方式二：交互式登录部署

### 1. 登录 Vercel

```bash
cd /home/user/webapp
npx vercel login
```

会提示选择登录方式：
- GitHub
- GitLab  
- Bitbucket
- Email

选择后按照提示完成登录。

### 2. 首次部署（设置项目）

```bash
npx vercel
```

会询问：
```
? Set up and deploy "~/webapp"? [Y/n] y
? Which scope do you want to deploy to? Your Account
? Link to existing project? [y/N] n
? What's your project's name? hubnote-vercel
? In which directory is your code located? ./
```

回答完成后会自动部署到预览环境。

### 3. 部署到生产环境

```bash
npx vercel --prod
```

---

## 🎯 实际操作步骤

### 如果你现在就要部署：

#### 步骤 1：我需要你提供 Token

请访问：https://vercel.com/account/tokens
创建 Token 后，告诉我 Token 值（格式类似：`xxxxxxxxxxxxxxxxxxxxxxxx`）

#### 步骤 2：我会执行部署命令

```bash
cd /home/user/webapp
export VERCEL_TOKEN=your_token_here
npx vercel --prod
```

#### 步骤 3：设置环境变量

部署后，需要在 Vercel Dashboard 设置环境变量：
1. 访问 https://vercel.com/dashboard
2. 找到 `hubnote-vercel` 项目
3. Settings → Environment Variables
4. 添加必需的环境变量（见下文）

---

## ⚙️ 必需的环境变量

在 Vercel Dashboard 添加以下环境变量：

```bash
# 1. SECRET_KEY
SECRET_KEY=320643ab5794568ef0021a1b7bf3d118a6ad9b3c44d59483bfec537f893fadfa

# 2. STORAGE_TYPE
STORAGE_TYPE=vercel_blob

# 3. BLOB_READ_WRITE_TOKEN（需要先创建 Blob Storage）
BLOB_READ_WRITE_TOKEN=<从 Storage 面板获取>

# 4. 可选
FLASK_ENV=production
FLASK_DEBUG=False
```

### 获取 BLOB_READ_WRITE_TOKEN：

1. 在项目页面，点击 "Storage" 标签
2. 点击 "Create" → 选择 "Blob"
3. 命名：`hubnote-storage`
4. 创建后复制 Token
5. 添加到环境变量

---

## 📊 部署后检查

### 1. 查看部署状态
```bash
npx vercel ls
```

### 2. 查看部署日志
```bash
npx vercel logs <deployment-url>
```

### 3. 访问应用
- 生产环境：https://hubnote-vercel.vercel.app
- 预览环境：https://hubnote-vercel-xxx.vercel.app

---

## 🔄 后续部署

环境变量设置完成后，后续部署非常简单：

```bash
# 1. 提交代码到 Git
git add .
git commit -m "your changes"
git push origin main

# 2. 部署到 Vercel
cd /home/user/webapp
./deploy-vercel.sh --prod
```

---

## ❓ 我应该选择哪种方式？

### 推荐：GitHub 自动部署 ⭐
- ✅ 最简单
- ✅ 自动化
- ✅ 有部署历史
- ✅ 支持回滚
- ❌ 需要授权 GitHub

### CLI 手动部署
- ✅ 完全控制
- ✅ 适合测试
- ✅ 可本地验证
- ❌ 需要手动执行
- ❌ 需要 Token 管理

---

## 💡 提示

1. **首次部署推荐使用 GitHub 自动部署**
   - 更简单
   - 更可靠
   - 自动化程度高

2. **CLI 部署适合**
   - 临时测试
   - 快速验证
   - CI/CD 集成

3. **两种方式可以混用**
   - GitHub 用于正常开发
   - CLI 用于紧急修复

---

## 📞 等待你的指令

请告诉我：
1. 你想使用哪种部署方式？
   - [ ] GitHub 自动部署（推荐）
   - [ ] CLI 手动部署（需要 Token）

2. 如果选择 CLI，请提供：
   - [ ] Vercel Token
   - [ ] 或选择交互式登录（我无法完成交互式操作）

3. 我可以帮你：
   - ✅ 执行部署命令
   - ✅ 检查部署状态
   - ✅ 查看部署日志
   - ✅ 解决部署问题
