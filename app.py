#!/usr/bin/env python3
"""Streamlit Web UI for PDF to Markdown converter."""

import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional, List
from queue import Queue, Empty

import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="PDF to Markdown Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


class ProcessingTask:
    """Processing task to track progress."""
    def __init__(self):
        self.running = False
        self.cancel_requested = False
        self.log_queue = Queue()
        self.completed = False
        self.error: Optional[str] = None


def process_pdfs(
    input_dir: str,
    output_dir: str,
    enable_ocr: bool,
    output_formats: List[str],
    hybrid_mode: str,
    task: ProcessingTask,
):
    """Run the PDF conversion in a background thread."""
    try:
        from opendataloader_pdf import convert
        import torch

        task.log_queue.put(f"Starting conversion...")
        task.log_queue.put(f"Input directory: {input_dir}")
        task.log_queue.put(f"Output directory: {output_dir}")

        # Check CUDA
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_name = torch.cuda.get_device_name()
            task.log_queue.put(f"✓ CUDA available: {device_name}")
        else:
            task.log_queue.put("⚠ CUDA not available, using CPU (slower)")

        # Find all PDF files
        input_path = Path(input_dir)
        pdf_files = list(input_path.glob("*.pdf"))

        if not pdf_files:
            task.log_queue.put(f"⚠ No PDF files found in {input_dir}")
            task.completed = True
            task.running = False
            return

        task.log_queue.put(f"Found {len(pdf_files)} PDF file(s) to process")

        # Build format list
        formats = []
        if "markdown" in output_formats:
            formats.append("markdown-with-images")
        if "json" in output_formats:
            formats.append("json")

        if not formats:
            formats = ["markdown-with-images"]

        # Process each PDF
        success_count = 0
        for i, pdf_file in enumerate(pdf_files, 1):
            if task.cancel_requested:
                task.log_queue.put("⛔ Conversion canceled by user")
                task.completed = True
                task.running = False
                return

            task.log_queue.put(f"--- Processing {i}/{len(pdf_files)}: {pdf_file.name} ---")

            try:
                convert_kwargs = dict(
                    input_path=str(pdf_file),
                    output_dir=str(Path(output_dir) / pdf_file.stem),
                    format=formats,
                    image_output="external",
                    image_format="png",
                    quiet=False,
                )

                if enable_ocr:
                    task.log_queue.put(f"OCR hybrid mode enabled: docling-fast")
                    convert_kwargs["hybrid"] = "docling-fast"
                    convert_kwargs["hybrid_mode"] = hybrid_mode
                    convert_kwargs["hybrid_fallback"] = True

                convert(**convert_kwargs)
                success_count += 1
                task.log_queue.put(f"✓ Completed: {pdf_file.name}")

            except Exception as e:
                task.log_queue.put(f"✗ Error processing {pdf_file.name}: {str(e)}")

        task.log_queue.put(f"--- All done! Completed {success_count}/{len(pdf_files)} file(s) ---")
        task.completed = True

    except Exception as e:
        task.log_queue.put(f"✗ Fatal error: {str(e)}")
        task.error = str(e)
        task.completed = True

    task.running = False


def main():
    """Main Streamlit app."""
    st.title("📄 PDF to Markdown Converter")
    st.markdown("使用 `opendataloader-pdf` 将 PDF 转换为高质量 Markdown，支持 OCR 扫描版 PDF")

    # 初始化 session state
    if "task" not in st.session_state:
        st.session_state.task = None

    # Get default paths based on project structure
    project_root = Path(__file__).parent
    default_input = str(project_root / "data" / "input")
    default_output = str(project_root / "data" / "output")

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ 配置设置")

        # Input directory
        input_dir = st.text_input(
            "📂 输入 PDF 目录",
            value=default_input,
            help="包含 PDF 文件的文件夹路径"
        )

        # Output directory
        output_dir = st.text_input(
            "📂 输出目录",
            value=default_output,
            help="转换后文件保存的文件夹路径"
        )

        st.divider()

        # OCR settings
        enable_ocr = st.checkbox(
            "🔍 启用 OCR 混合模式",
            value=True,
            help="对扫描版 PDF 进行 OCR 文字识别，需要 GPU 加速"
        )

        if enable_ocr:
            hybrid_mode = st.radio(
                "OCR 混合模式",
                options=["auto", "full"],
                index=0,
                help="auto: 仅对需要 OCR 的页面使用 AI (推荐)\nfull: 所有页面都使用 AI 处理"
            )
        else:
            hybrid_mode = "auto"

        st.divider()

        # Output format
        output_formats = st.multiselect(
            "📝 输出格式",
            options=["markdown", "json"],
            default=["markdown"],
            help="markdown-with-images: Markdown 并提取图片\njson: 结构化 JSON 输出"
        )

        st.divider()

        # GPU info
        try:
            import torch
            if torch.cuda.is_available():
                st.success(f"✅ GPU 可用: {torch.cuda.get_device_name()}")
            else:
                st.warning("⚠️ GPU 不可用，使用 CPU (较慢)")
        except:
            st.warning("⚠️ PyTorch 未正确安装")

    # Main area - Log output
    st.header("📋 处理日志")

    # Control buttons
    col1, col2 = st.columns(2)

    with col1:
        start_button = st.button(
            "▶️ 开始转换",
            disabled=st.session_state.task is not None and st.session_state.task.running,
            use_container_width=True
        )

    with col2:
        cancel_button = st.button(
            "⏹️ 取消",
            disabled=st.session_state.task is None or not st.session_state.task.running,
            use_container_width=True
        )

    # Create a placeholder for logs
    log_placeholder = st.empty()

    # Handle start
    if start_button:
        # Validate paths
        if not Path(input_dir).exists():
            st.error(f"输入目录不存在: {input_dir}")
            return

        if not Path(output_dir).exists():
            Path(output_dir).mkdir(parents=True)
            st.info(f"创建输出目录: {output_dir}")

        # Create new task
        task = ProcessingTask()
        task.running = True
        st.session_state.task = task

        # Start background thread
        thread = threading.Thread(
            target=process_pdfs,
            args=(input_dir, output_dir, enable_ocr, output_formats, hybrid_mode, task),
            daemon=True
        )
        thread.start()

    # Handle cancel
    if cancel_button and st.session_state.task is not None:
        st.session_state.task.cancel_requested = True
        st.info("取消请求已发送，正在停止...")

    # Update logs
    if st.session_state.task is not None:
        task = st.session_state.task
        logs = []

        # Get all new logs
        while True:
            try:
                msg = task.log_queue.get_nowait()
                logs.append(msg)
            except Empty:
                break

        # Display logs in a scrollable container
        if logs:
            log_text = "\n".join(logs)
            log_placeholder.code(log_text, language="text")

        # Check if completed
        if task.completed:
            if task.error:
                st.error(f"转换出错: {task.error}")
            else:
                st.success("转换完成!")

        # Rerun to update UI
        if task.running or (task.completed and logs):
            time.sleep(0.5)
            st.rerun()

    else:
        log_placeholder.info("点击「开始转换」开始处理 PDF...")

    # Help section
    with st.expander("ℹ️ 使用说明"):
        st.markdown("""
        ### 使用说明

        1. **选择输入目录**：放置你的 PDF 文件在该目录下
        2. **选择输出目录**：转换后的文件会保存在这里
        3. **OCR 设置**：
           - 如果是扫描版 PDF，勾选「启用 OCR 混合模式」
           - `auto` 模式：智能判断哪些页面需要 OCR，速度更快（推荐）
           - `full` 模式：所有页面都用 AI OCR 处理，质量更好但速度慢
        4. **输出格式**：可同时选择 Markdown 和 JSON
        5. 点击「开始转换」即可开始

        ### 输出说明

        - **Markdown**: `{输出目录}/{pdf_name}/{pdf_name}.md`
        - **图片**: `{输出目录}/{pdf_name}/images/`
        - **JSON**: `{输出目录}/{pdf_name}/{pdf_name}.json`

        ### 提示

        - OCR 需要 PyTorch GPU 支持，你的 RTX 4050 会自动使用
        - Java 必须正确安装并在 PATH 中
        """)


if __name__ == "__main__":
    main()
