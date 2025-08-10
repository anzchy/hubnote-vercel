# HubNote 启动指南

## 打包后的应用使用方法

### 方法一：双击启动（推荐）
1. 双击 `dist/HubNote.app` 启动应用
2. 应用会自动在后台运行，默认端口为 5001
3. 打开浏览器访问：http://127.0.0.1:5001
4. 首次使用需要配置 GitHub Token

### 方法二：命令行启动
```bash
# 进入应用目录
cd dist/HubNote.app/Contents/MacOS/

# 直接运行
./HubNote
```

## 配置 GitHub Token

### 首次启动配置
1. 启动应用后，浏览器会自动重定向到配置页面
2. 在配置页面输入你的 GitHub Personal Access Token
3. 点击「保存配置」按钮
4. 系统会自动验证 Token 的有效性

### GitHub Token 获取方法
1. 登录 GitHub，进入 Settings > Developer settings > Personal access tokens
2. 点击 "Generate new token (classic)"
3. 选择以下权限：
   - `repo` - 访问私有仓库
   - `public_repo` - 访问公共仓库
   - `read:user` - 读取用户信息
4. 生成并复制 Token

### 配置文件位置
- 用户配置文件保存在：`~/Library/Application Support/HubNote/config.json`
- 可以手动编辑此文件来修改配置

## 故障排除

### 应用无法启动
1. 确保系统版本：macOS 10.15 或更高版本
2. 检查端口占用：确保端口 5001 未被其他应用占用
3. 查看系统日志：`log show --predicate 'process == "HubNote"' --last 5m`

### 无法访问 GitHub
1. 检查网络连接
2. 验证 GitHub Token 是否有效
3. 确认 Token 权限设置正确

### 端口冲突
- 打包后的应用默认使用端口 5001
- 开发模式使用端口 5000
- 如需修改端口，可通过命令行参数：`./HubNote --port 8080`

## 注意事项

1. **Apple Silicon 兼容性**：应用已针对 M1/M2/M3/M4 芯片优化
2. **安全提示**：首次运行可能提示"无法验证开发者"，需要在系统偏好设置中允许运行
3. **数据存储**：应用数据保存在用户目录下，卸载应用不会删除配置文件
4. **多进程警告**：命令行运行时可能出现多进程相关警告，这是正常现象，不影响功能

## 开发模式

如需进行开发或调试，可以使用源码方式运行：

```bash
# 激活虚拟环境
source gitnote-venv/bin/activate

# 运行开发服务器
python run.py --debug
```

开发模式会在端口 5000 上运行，支持热重载和调试功能。