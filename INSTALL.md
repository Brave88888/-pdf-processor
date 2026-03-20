# PDF Processor 一键安装说明

本项目提供 **单文件一键安装包**，双击即可自动完成全部安装过程。

## 📋 系统要求

- **操作系统**: Windows 10 / Windows 11
- **Python**: Python 3.10 或更高版本 ([下载Python](https://www.python.org/downloads/))
- **内存**: 至少 8 GB RAM (推荐 16 GB)
- **磁盘空间**: 至少 5 GB 可用空间 (用于存放依赖库，包括PyTorch)
- **网络**: 需要联网下载依赖包

## 📥 下载

从发布页下载 **`pdf-processor-installer.exe`** (约 22 MB)，这就是唯一需要的文件。

## 🚀 一键安装

1. **双击运行 `pdf-processor-installer.exe`**

2. **等待自动安装完成**，安装程序会自动：
   - ✅ 检查Python版本
   - ✅ 解压所有文件到 `%LOCALAPPDATA%\pdf-processor`
   - ✅ 使用 uv 创建虚拟环境
   - ✅ 安装所有依赖包 (需要几分钟时间，请耐心等待)
   - ✅ 在桌面创建快捷方式

3. **安装完成后**，可以选择立即启动 Web UI。

## 🎯 使用方法

安装完成后，桌面会出现两个快捷方式：

### 1. 图形界面 (推荐) - **PDF Processor (Web UI)**

双击桌面的 **`PDF Processor (Web UI)`** 快捷方式，会自动：
- 激活虚拟环境
- 启动 Streamlit Web 界面
- 自动在浏览器打开应用

> 默认地址: http://localhost:8501

### 2. 命令行 - **PDF Processor (CLI)**

双击桌面的 **`PDF Processor (CLI)`** 快捷方式，会启动命令行界面，你可以：

```bash
# 转换单个PDF文件
python main.py --input your_file.pdf --output output.md

# 批量转换目录下所有PDF
python main.py --input ./pdfs --output ./output
```

## 🔧 安装位置

默认安装位置：
```
%LOCALAPPDATA%\pdf-processor\
```

你可以在环境变量 `INSTALL_DIR` 中指定自定义安装路径，然后运行安装程序：

```batch
set INSTALL_DIR=D:\apps\pdf-processor
pdf-processor-installer.exe
```

## ❓ 常见问题

### Q: 安装需要多久？

A: 首次安装需要下载约 2GB 的依赖包 (主要是PyTorch)，根据网络速度，大约需要 5-15 分钟。

### Q: 可以离线安装吗？

A: 安装包内置了 uv，但是依赖包仍然需要联网下载。如果你需要完全离线安装，请提前下载好依赖包。

### Q: 如何卸载？

A:
1. 删除桌面的两个快捷方式
2. 删除安装文件夹：`%LOCALAPPDATA%\pdf-processor`
3. 就完成了，安装程序不会修改注册表或系统目录

### Q: 提示 "Python 版本过低"

A: 需要安装 Python 3.10 或更新版本，请到 https://www.python.org/downloads/ 下载最新版。

### Q: 安装过程中提示 "依赖安装失败"

A:
- 检查网络连接是否正常
- 确保有足够的磁盘空间
- 尝试重新运行安装程序
- 如果使用代理，请确保系统代理设置正确

### Q: GPU 支持？

A: 安装程序会自动检测你的NVIDIA显卡，如果CUDA可用，uv会自动安装GPU版本的PyTorch。可以运行 `check_gpu.py` 检查：

```bash
cd %LOCALAPPDATA%\pdf-processor\pdf-processor
call .venv\Scripts\activate.bat
python check_gpu.py
```

## 📝 说明

- 安装包使用 Windows 自带的 CAB 压缩，无需第三方解压软件
- 使用 uv 进行依赖管理，安装更快，更可靠
- 所有操作都在用户目录下完成，不需要管理员权限

---

安装完成后打开 Web UI 就可以开始转换PDF了！
