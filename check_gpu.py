#!/usr/bin/env python3
"""Check if GPU/CUDA is available and working correctly with PyTorch."""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Check GPU availability and print information."""
    try:
        import torch
        logger.info("=" * 60)
        logger.info("PyTorch GPU/CUDA Check")
        logger.info("=" * 60)
        logger.info(f"PyTorch version: {torch.__version__}")

        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA available: {cuda_available}")

        if cuda_available:
            device_count = torch.cuda.device_count()
            logger.info(f"Number of CUDA devices: {device_count}")

            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_prop = torch.cuda.get_device_properties(i)
                total_mem_gb = device_prop.total_memory / (1024 ** 3)
                logger.info(f"  Device {i}: {device_name}, {total_mem_gb:.2f} GB memory")

            # 测试简单张量计算在 CUDA 上
            logger.info("Testing CUDA tensor computation...")
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = torch.matmul(x, y)
            logger.info(f"✓ CUDA matrix multiplication succeeded, result shape: {z.shape}")
            logger.info("")
            logger.info("✓ GPU is working correctly! You can use CUDA acceleration.")
        else:
            logger.warning("✗ CUDA is not available. The conversion will fall back to CPU, which will be slower.")
            logger.info("Please check your PyTorch installation and CUDA setup.")

        logger.info("=" * 60)

    except ImportError:
        logger.error("✗ PyTorch is not installed. Please run: uv pip install torch torchvision")
    except Exception as e:
        logger.error(f"✗ Error during GPU check: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
