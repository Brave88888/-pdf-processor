#!/usr/bin/env python3
"""PDF to Markdown converter using opendataloader-pdf."""

import logging
import os
import sys
from pathlib import Path
from typing import List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def find_pdf_files(input_dir: Path) -> List[Path]:
    """Find all PDF files in the input directory."""
    pdf_files = list(input_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF file(s) in {input_dir}")
    return pdf_files


def process_pdf(pdf_path: Path, output_dir: Path, cuda_available: bool, enable_ocr: bool = True) -> None:
    """Process a single PDF file and convert to Markdown.

    Args:
        pdf_path: Path to the input PDF file
        output_dir: Output directory
        cuda_available: Whether CUDA GPU is available
        enable_ocr: Enable OCR/hybrid mode for scanned/OCR PDFs (default: True)
    """
    try:
        from opendataloader_pdf import convert

        logger.info(f"Processing: {pdf_path.name}")

        # 使用 opendataloader-pdf convert API 进行转换
        # 输出格式: markdown-with-images (包含图片提取)
        convert_kwargs = dict(
            input_path=str(pdf_path),
            output_dir=str(output_dir / pdf_path.stem),
            format=["markdown-with-images"],
            image_output="external",
            image_format="png",
            quiet=False,
        )

        # 启用 OCR 混合模式处理扫描版 PDF
        if enable_ocr:
            logger.info("OCR hybrid mode enabled (docling-fast) for scanned/OCR PDF")
            # 使用 docling-fast 混合后端进行 OCR 识别
            # docling 使用 PyTorch 模型进行文本定位和 OCR 识别
            convert_kwargs["hybrid"] = "docling-fast"
            convert_kwargs["hybrid_mode"] = "auto"  # 动态分流：仅需要 OCR 的页面使用 AI
            convert_kwargs["hybrid_fallback"] = True  # 如果 AI 出错，回退到原生处理
            # 使用 GPU 加速
            if cuda_available:
                logger.info(f"GPU acceleration will be used for OCR")

        convert(**convert_kwargs)

        logger.info(f"Completed conversion for: {pdf_path.name}")

    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Please make sure all dependencies are installed: uv pip install opendataloader-pdf torch torchvision")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing {pdf_path.name}: {str(e)}", exc_info=True)
        raise


def check_gpu() -> bool:
    """Check if GPU/CUDA is available."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            device_name = torch.cuda.get_device_name(current_device)
            logger.info(f"CUDA is available: {device_count} device(s) detected")
            logger.info(f"Current device: {device_name}")
        else:
            logger.warning("CUDA is not available, will use CPU instead")
        return cuda_available
    except ImportError:
        logger.error("PyTorch is not installed")
        return False
    except Exception as e:
        logger.error(f"Error checking GPU: {str(e)}")
        return False


def main():
    """Main function to process all PDF files in data/input."""
    # 获取项目根目录
    project_root = Path(__file__).parent
    input_dir = project_root / "data" / "input"
    output_dir = project_root / "data" / "output"

    # 创建输出目录（如果不存在）
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("PDF to Markdown Converter")
    logger.info("=" * 60)

    # 检查 GPU
    has_gpu = check_gpu()
    logger.info("")

    # 找到所有 PDF 文件
    pdf_files = find_pdf_files(input_dir)

    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}. Please add PDF files to data/input folder.")
        return

    # 处理每个 PDF 文件
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info("-" * 60)
        logger.info(f"Processing file {i}/{len(pdf_files)}")
        # 默认启用 OCR 混合模式处理扫描版 PDF
        process_pdf(pdf_file, output_dir, cuda_available=has_gpu, enable_ocr=True)
        logger.info(f"Completed file {i}/{len(pdf_files)}")

    logger.info("-" * 60)
    logger.info("All processing completed!")
    logger.info(f"Output files are saved in: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
