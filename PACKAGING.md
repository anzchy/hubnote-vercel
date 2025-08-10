# HubNote 应用打包指南

本指南介绍如何将 HubNote Flask 应用打包为独立的 macOS 应用程序。

## 打包方案

我们使用 **PyInstaller** 作为主要打包工具，它是目前最成熟和广泛使用的 Python 应用打包解决方案。

## 快速开始

### 方法一：使用自动化脚本（推荐）

```bash
# 直接运行打包脚本
./build_app.sh
```

### 方法二：手动打包

1. **安装 PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **激活虚拟环境**（如果使用）
   ```bash
   source gitnote-venv/bin/activate
   ```

3. **执行打包命令**
   ```bash
   pyinstaller HubNote.spec
   ```

## 打包配置说明

### HubNote.spec 文件

这是 PyInstaller 的配置文件，包含以下关键配置：

- **入口文件**: `run.py`
- **数据文件**: 包含 `templates/`, `static/`, `data/`, `.env`
- **隐藏导入**: 确保所有依赖模块被正确包含
- **应用信息**: 设置应用名称、版本、Bundle ID 等

### 关键修改

为了支持打包，我们对 `app.py` 进行了以下修改：

```python
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持 PyInstaller 打包"""
    try:
        base_path = sys._MEIPASS  # PyInstaller 临时目录
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
```

## 打包结果

成功打包后，您将在 `dist/` 目录下找到：

- `HubNote.app` - 完整的 macOS 应用程序包

## 使用打包后的应用

### 安装

1. 将 `HubNote.app` 拖拽到 `Applications` 文件夹
2. 或者直接双击运行

### 运行

```bash
# 命令行运行
open dist/HubNote.app

# 或直接双击应用图标
```

## 注意事项

### 环境配置

- 确保 `.env` 文件包含正确的 GitHub Token
- 打包后的应用会包含 `.env` 文件，注意安全性

### 文件权限

- 首次运行可能需要在「系统偏好设置 > 安全性与隐私」中允许运行
- 如果遇到权限问题，可以右键点击应用选择「打开」

### 性能优化

- 打包后的应用启动可能比开发模式稍慢
- 应用大小约为 50-100MB（包含 Python 运行时）

## 故障排除

### 常见问题

1. **模块导入错误**
   - 检查 `HubNote.spec` 中的 `hiddenimports` 列表
   - 添加缺失的模块到隐藏导入中

2. **静态文件找不到**
   - 确认 `datas` 配置正确包含了所有必要文件
   - 检查 `get_resource_path` 函数是否正确使用

3. **应用无法启动**
   - 查看控制台日志：`Console.app`
   - 检查 `.env` 文件是否存在且配置正确

### 调试模式

如需调试打包后的应用，可以修改 `HubNote.spec`：

```python
exe = EXE(
    # ...
    console=True,  # 显示控制台窗口
    debug=True,    # 启用调试模式
    # ...
)
```

## 高级配置

### 添加应用图标

1. 准备 `.icns` 格式的图标文件
2. 在 `HubNote.spec` 中设置 `icon` 参数

### 代码签名（可选）

如需发布到 Mac App Store 或避免安全警告：

```python
exe = EXE(
    # ...
    codesign_identity='Developer ID Application: Your Name',
    # ...
)
```

## 总结

HubNote 现在可以轻松打包为独立的 macOS 应用程序，用户无需安装 Python 环境即可使用。打包后的应用保持了原有的所有功能，并提供了更好的用户体验。