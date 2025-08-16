# Vercel 部署问题解决指南

## 问题1：添加用户失败

### 症状
- 本地开发环境可以正常添加用户
- Vercel部署后显示"添加用户失败"

### 原因分析
1. **存储配置问题** - Vercel环境中的存储类型配置不正确
2. **环境变量缺失** - 缺少必要的Vercel KV配置
3. **权限问题** - Vercel KV的访问权限配置有误

### 解决步骤

#### 步骤1：检查Vercel环境变量
在Vercel项目设置中添加以下环境变量：

```bash
# 存储类型
STORAGE_TYPE=vercel_kv

# Vercel KV 配置
KV_REST_API_URL=https://your-project.vercel.app/api/kv
KV_REST_API_TOKEN=your_kv_token

# 其他必要配置
GITHUB_TOKEN=your_github_token
SECRET_KEY=your_secret_key
```

#### 步骤2：配置Vercel KV
1. 在Vercel控制台创建KV数据库
2. 获取KV的REST API URL和Token
3. 确保KV数据库有读写权限

#### 步骤3：验证配置
使用提供的检查脚本验证配置：

```bash
python vercel_env_check.py
```

#### 步骤4：临时解决方案
如果KV配置有问题，可以临时使用内存存储：

```bash
STORAGE_TYPE=memory
```

**注意：** 内存存储在Vercel环境中重启后会丢失数据

## 问题2：非管理员用户看到所有仓库

### 症状
- 普通用户登录后看到管理员添加的所有仓库
- 权限控制不生效

### 原因分析
- 系统没有按用户权限过滤仓库列表
- 缺少用户权限验证逻辑

### 解决方案

#### 已修复的功能
1. **用户权限过滤** - 普通用户只能看到自己添加的仓库
2. **管理员权限** - 管理员可以看到所有仓库
3. **仓库归属记录** - 添加仓库时记录添加者信息

#### 验证修复
1. 使用管理员账户添加仓库
2. 使用普通用户账户登录
3. 检查是否只显示自己添加的仓库

## 部署检查清单

### 环境变量
- [ ] `STORAGE_TYPE` 设置正确
- [ ] `KV_REST_API_URL` 已配置
- [ ] `KV_REST_API_TOKEN` 已配置
- [ ] `GITHUB_TOKEN` 已配置
- [ ] `SECRET_KEY` 已配置

### Vercel配置
- [ ] KV数据库已创建
- [ ] KV权限配置正确
- [ ] 项目已重新部署

### 功能测试
- [ ] 用户登录正常
- [ ] 添加用户功能正常
- [ ] 仓库权限控制正常
- [ ] 用户管理功能正常

## 常见错误及解决方案

### 错误1：ModuleNotFoundError
**原因：** 依赖包未正确安装
**解决：** 检查`requirements.txt`和Vercel构建配置

### 错误2：存储操作失败
**原因：** 存储配置不正确
**解决：** 检查环境变量和KV配置

### 错误3：权限验证失败
**原因：** 认证配置问题
**解决：** 检查SECRET_KEY和GitHub Token

## 调试技巧

### 1. 查看Vercel日志
```bash
vercel logs your-project-name
```

### 2. 使用环境检查脚本
```bash
python vercel_env_check.py
```

### 3. 检查网络请求
在浏览器开发者工具中查看网络请求状态

### 4. 临时启用调试模式
在Vercel环境中临时设置：
```bash
FLASK_DEBUG=true
```

## 联系支持

如果问题仍然存在，请提供：
1. Vercel部署日志
2. 环境检查脚本输出
3. 具体的错误信息
4. 复现步骤

## 更新日志

- 2025-08-16: 添加用户权限过滤功能
- 2025-08-16: 修复仓库显示权限问题
- 2025-08-16: 添加Vercel环境检查脚本
- 2025-08-16: 完善错误处理和调试信息
