#!/usr/bin/env python3
"""
FLUX Coloring Book Generator
Professional AI-powered coloring book creation tool
"""

import sys
import os
import logging
from pathlib import Path

def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('coloring_book.log')
        ]
    )

def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🎨 FLUX Coloring Book Generator Starting...")
    
    # Add src directory to path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    # Check if GUI is available (for server environments)
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        logger.info("GUI mode available")
        
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)
        app.setApplicationName("FLUX Coloring Book Generator")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("3D Gravity Kids")
        app.setOrganizationDomain("kopshtimagjik.com")
        
        # Initialize configuration
        from core.app_config import AppConfig
        config = AppConfig()
        
        # Create main window
        from ui.main_window import MainWindow
        window = MainWindow(config)
        window.show()
        
        logger.info("GUI application started")
        return app.exec()
        
    except ImportError as e:
        logger.info("GUI not available, starting server mode")
        return run_server_mode()

def run_server_mode():
    """Run in server mode (no GUI)"""
    logger = logging.getLogger(__name__)
    
    try:
        from models.flux_loader import FluxModelLoader
        import torch
        
        # Check system
        logger.info("=== System Check ===")
        logger.info(f"Python: {sys.version}")
        logger.info(f"PyTorch: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB")
        
        # Initialize FLUX loader
        logger.info("Initializing FLUX model loader...")
        loader = FluxModelLoader()
        
        # Check models
        model_status = loader.check_models()
        if not all(model_status.values()):
            logger.error("Missing models! Please check models/ directory")
            return 1
        
        # Test generation (optional)
        logger.info("Server mode ready. Use server_main.py for API server.")
        return 0
        
    except Exception as e:
        logger.error(f"Server mode failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())