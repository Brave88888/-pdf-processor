# PDF to Markdown Processor

使用 `opendataloader-pdf` 将 PDF 批量转换为高质量 Markdown 格式，支持 GPU 加速。

## 项目结构

```
pdf-processor/
├── data/
│   ├── input/          # 放入需要转换的 PDF 文件
│   └── output/         # 转换后的 Markdown 和图片会保存在这里
├── main.py             # 主程序
├── check_gpu.py        # GPU 环境检查脚本
└── pyproject.toml      # 项目依赖
```

## 环境安装

本项目使用 `uv` 进行包管理：

```bash
# 创建虚拟环境并安装依赖
uv sync
```

如果你需要手动安装：

```bash
uv pip install opendataloader-pdf torch torchvision
```

## 使用方法

### 命令行方式

1. 将需要转换的 PDF 文件放入 `data/input/` 文件夹
2. 运行转换程序：

```bash
python main.py
```

3. 转换后的 Markdown 文件会输出到 `data/output/` 文件夹，图片会保存在对应名称的 `images/` 子文件夹中。

### 网页 UI 方式 (推荐)

启动 Streamlit 网页界面：

```bash
streamlit run app.py
```

然后在浏览器中打开显示的本地地址（默认为 http://localhost:8501），你可以：

- 选择输入/输出目录
- 勾选是否启用 OCR 混合模式
- 选择 OCR 混合模式（auto / full）
- 选择输出格式（Markdown / JSON）
- 实时查看处理日志
- 随时取消处理

网页界面截图：

![Web UI](docs/web-ui.png)

## 检查 GPU 环境

运行环境检查脚本确认 GPU 是否可用：

```bash
python check_gpu.py
```

如果输出 `CUDA available: True` 说明 GPU 可以正常使用，转换速度会更快。

## 配置说明

- **OCR 支持**：默认启用 `hybrid=docling-fast` 混合模式，自动对扫描版/OCR PDF 进行 AI 识别
- 默认使用 GPU 加速 OCR 处理（如果 CUDA 可用）
- 如果没有可用 GPU，OCR 会回退到 CPU 计算（速度会慢一些）
- 动态分流模式 (`hybrid_mode=auto`)：只对需要 OCR 的页面使用 AI 处理，保持速度
- 程序会自动处理所有 `data/input/` 根目录下的 `.pdf` 文件
- 提取出的图片会保存在 `data/output/<pdf_name>/images/` 目录

## 依赖

- Python >= 3.10
- opendataloader-pdf
- PyTorch >= 2.0.0 (with CUDA support recommended)
- torchvision
