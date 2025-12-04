# Vercel KV 存储配置指南

## 📋 问题背景

Vercel 的文件系统是**只读**的，无法使用本地文件存储数据。因此必须使用 Vercel 提供的存储服务。

## 🎯 推荐方案：Vercel KV

Vercel KV 是基于 Redis 的键值对存储服务，非常适合存储应用配置和状态数据。

### 为什么选择 KV 而不是 Blob？

| 特性 | Vercel KV | Vercel Blob |
|------|-----------|-------------|
| 适用场景 | 键值对数据、配置、状态 | 大文件、图片、视频 |
| 读写速度 | 极快（Redis） | 较慢（对象存储） |
| 数据结构 | 简单键值对 | 文件对象 |
| 成本 | 按请求计费 | 按存储空间计费 |
| 我们的用例 | ✅ **推荐** | ⚠️ 可用但不推荐 |

## 🚀 配置步骤

### 1. 创建 Vercel KV 数据库

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 进入你的项目
3. 点击 **Storage** 标签
4. 点击 **Create Database**
5. 选择 **KV (Redis)**
6. 输入数据库名称（例如：`hubnote-kv`）
7. 选择区域（推荐选择离用户最近的区域）
8. 点击 **Create**

### 2. 连接 KV 到项目

创建后，Vercel 会自动将 KV 连接到你的项目，并自动添加以下环境变量：

- `KV_REST_API_URL` - KV REST API 端点
- `KV_REST_API_TOKEN` - KV 访问令牌
- `KV_REST_API_READ_ONLY_TOKEN` - 只读令牌（可选）
- `KV_URL` - Redis 连接 URL（可选，如果使用 Redis 客户端）

### 3. 更新环境变量

在 Vercel Dashboard → Settings → Environment Variables 中确认以下环境变量已设置：

```bash
# 存储配置
STORAGE_TYPE=vercel_kv

# KV 连接信息（Vercel 自动生成）
KV_REST_API_URL=https://xxxxx.kv.vercel-storage.com
KV_REST_API_TOKEN=xxxxx

# Flask 配置
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
FLASK_DEBUG=False
```

### 4. 重新部署

环境变量更新后，需要重新部署项目：

```bash
# 方法1: 使用 Git 推送（推荐）
git push origin main

# 方法2: 在 Vercel Dashboard 手动触发部署
# 进入 Deployments → 点击三个点 → Redeploy
```

## 🧪 验证配置

部署完成后，检查日志应该看到：

```
StorageManager 初始化:
  - 运行环境: Vercel
  - 存储类型: vercel_kv
  - KV URL: https://xxxxx.kv.vercel-storage.com
  - KV Token: 已设置
  - Blob Token: 未设置
```

## 🔧 本地开发配置

在本地开发时，你可以：

### 选项 1: 使用本地文件存储（推荐）

创建 `.env` 文件：

```bash
STORAGE_TYPE=file
FLASK_ENV=development
SECRET_KEY=dev_secret_key_for_local_testing
```

### 选项 2: 使用 Vercel KV（需要网络）

从 Vercel Dashboard 复制 KV 凭据到 `.env`：

```bash
STORAGE_TYPE=vercel_kv
KV_REST_API_URL=https://xxxxx.kv.vercel-storage.com
KV_REST_API_TOKEN=xxxxx
SECRET_KEY=dev_secret_key_for_local_testing
```

## 📊 KV 使用成本

Vercel KV 定价（截至 2024）：

- **Hobby 计划**: 
  - 256 MB 存储
  - 3,000 次请求/天
  - **免费**

- **Pro 计划**:
  - 1 GB 存储
  - 100,000 次请求/月
  - 包含在订阅中

对于大多数个人项目，Hobby 计划完全够用。

## ⚠️ 常见问题

### Q1: 为什么我的数据没有保存？

检查日志中是否有以下错误：
- `Vercel 环境不支持文件存储` - 需要配置 KV
- `KV 写入失败: HTTP 401` - Token 无效或过期
- `使用内存存储 (数据不持久化)` - 未正确配置存储

### Q2: 如何清空 KV 数据？

在 Vercel Dashboard → Storage → 你的 KV 数据库 → 可以查看和删除键。

或使用 Vercel CLI：

```bash
# 安装 Vercel CLI
npm i -g vercel

# 连接到项目
vercel link

# 删除特定键
vercel kv del repos
```

### Q3: 如何查看 KV 中的数据？

在 Vercel Dashboard → Storage → 你的 KV 数据库 → Browse

或使用 Vercel CLI：

```bash
# 获取值
vercel kv get repos

# 列出所有键
vercel kv keys "*"
```

## 🔄 从 Blob 迁移到 KV

如果你之前使用了 Blob 存储，切换到 KV 后数据会丢失（它们在不同的存储系统中）。

迁移步骤：
1. 导出 Blob 中的数据（如果有）
2. 配置 KV
3. 重新添加仓库

由于这是新部署，不存在迁移问题。

## 📚 更多资源

- [Vercel KV 官方文档](https://vercel.com/docs/storage/vercel-kv)
- [Vercel KV REST API](https://vercel.com/docs/storage/vercel-kv/rest-api)
- [Vercel KV 定价](https://vercel.com/docs/storage/vercel-kv/usage-and-pricing)
