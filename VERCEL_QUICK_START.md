# 🚀 Vercel 快速部署指南

## ⚡ 5 分钟快速部署

### 第 1 步：打开 Vercel Dashboard
访问：https://vercel.com/new

### 第 2 步：导入 GitHub 仓库
1. 选择 "Import Git Repository"
2. 搜索并选择：`anzchy/hubnote-vercel`
3. 点击 "Import"

### 第 3 步：配置项目
保持默认设置：
- ✅ Framework Preset: Other
- ✅ Root Directory: `./`
- ✅ Build Command: (留空)
- ✅ Output Directory: (留空)

### 第 4 步：设置环境变量 ⚠️ 重要！

**必须添加的环境变量：**

```bash
# 1. SECRET_KEY（复制下面生成的值）
SECRET_KEY=320643ab5794568ef0021a1b7bf3d118a6ad9b3c44d59483bfec537f893fadfa

# 2. STORAGE_TYPE
STORAGE_TYPE=vercel_blob

# 3. BLOB_READ_WRITE_TOKEN（需要先创建 Blob Storage）
BLOB_READ_WRITE_TOKEN=<待填写>
```

**如何获取 BLOB_READ_WRITE_TOKEN：**

1. 在 Vercel 项目页面，点击 "Storage" 标签
2. 点击 "Create Database" → 选择 "Blob"
3. 给存储命名（例如：hubnote-storage）
4. 点击 "Create"
5. 创建后会显示环境变量，复制 `BLOB_READ_WRITE_TOKEN` 的值
6. 回到 "Settings" → "Environment Variables"
7. 添加 `BLOB_READ_WRITE_TOKEN` 变量

**可选环境变量：**

```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

### 第 5 步：部署
点击 "Deploy" 按钮，等待 1-2 分钟

### 第 6 步：访问应用
部署成功后，你会获得一个 URL：
- 例如：`https://hubnote-vercel.vercel.app`

---

## ✅ 部署后检查

访问你的部署 URL，检查以下功能：

- [ ] 网站可以打开
- [ ] 显示登录页面
- [ ] 可以使用 GitHub Token 登录
- [ ] 可以添加仓库
- [ ] 可以查看 Issues
- [ ] 可以查看和添加评论

---

## 🔧 如果遇到问题

### 问题 1：部署失败

**查看日志：**
1. 在 Vercel Dashboard 找到你的项目
2. 点击失败的部署
3. 查看 "Build Logs"

**常见原因：**
- 缺少环境变量
- Python 依赖安装失败
- `vercel.json` 配置错误

### 问题 2：页面打开但报错 500

**可能原因：**
- 缺少 `SECRET_KEY` 或 `BLOB_READ_WRITE_TOKEN`
- Blob Storage 未创建

**解决方案：**
1. 检查环境变量是否全部设置
2. 重新部署：Deployments → 最新部署 → "Redeploy"

### 问题 3：登录后看不到仓库

**原因：**
- 存储配置问题
- 环境变量未生效

**解决方案：**
1. 检查 `STORAGE_TYPE` 是否设置为 `vercel_blob`
2. 检查 `BLOB_READ_WRITE_TOKEN` 是否正确
3. 重新部署使环境变量生效

---

## 📱 绑定自定义域名（可选）

### 步骤：

1. 在 Vercel Dashboard，进入项目
2. 点击 "Settings" → "Domains"
3. 输入你的域名（例如：`hubnote.yourdomain.com`）
4. 点击 "Add"
5. 根据提示在你的 DNS 提供商添加记录：
   - **CNAME**: 指向 `cname.vercel-dns.com`
   - 或 **A**: 指向 Vercel 提供的 IP

---

## 🔄 自动部署

设置完成后，每次你推送代码到 GitHub 的 `main` 分支：
- ✅ Vercel 自动检测更新
- ✅ 自动构建和部署
- ✅ 约 1-2 分钟后生效

**查看部署历史：**
- Dashboard → Deployments

**回滚到之前的版本：**
- 选择一个历史部署
- 点击右上角 "⋯" → "Promote to Production"

---

## 🎯 下一步

1. **添加用户到白名单**
   - 以管理员身份登录
   - 访问 `/user-management`
   - 添加允许的用户

2. **备份重要数据**
   - 使用导出功能定期备份
   - 考虑设置定期备份脚本

3. **监控应用**
   - 定期查看 Vercel Analytics
   - 设置告警通知

---

## 📚 更多文档

- [完整部署指南](./DEPLOY_GUIDE.md)
- [Vercel 官方文档](https://vercel.com/docs)
- [项目 README](./README.md)

---

## 💬 需要帮助？

- 查看 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- 提交 Issue 到 GitHub
- 联系管理员

---

**祝部署顺利！🎉**
