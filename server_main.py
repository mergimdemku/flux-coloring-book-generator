#!/usr/bin/env python3
"""
FLUX Coloring Book Generator - Server Mode
Professional server deployment for RTX 5090
"""

import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def setup_logging():
    """Setup server logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Server main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 FLUX Coloring Book Generator - Server Mode")
    logger.info("=" * 60)
    
    try:
        from models.flux_loader import FluxModelLoader
        import torch
        
        # System information
        logger.info("=== System Information ===")
        logger.info(f"Python: {sys.version}")
        logger.info(f"PyTorch: {torch.__version__}")
        logger.info(f"CUDA: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"GPU: {gpu_name}")
            logger.info(f"VRAM: {vram_gb:.1f}GB")
            
            if "5090" in gpu_name:
                logger.info("✅ RTX 5090 detected - Ultimate performance mode")
            elif "4090" in gpu_name:
                logger.info("✅ RTX 4090 detected - High performance mode")
            else:
                logger.info("⚠️  Other GPU detected - Standard mode")
        
        # Initialize FLUX loader
        logger.info("\n=== FLUX Model Loading ===")
        loader = FluxModelLoader()
        
        # Show system info
        system_info = loader.get_system_info()
        for key, value in system_info.items():
            logger.info(f"{key}: {value}")
        
        # Check models
        logger.info("\n=== Model Check ===")
        model_status = loader.check_models()
        
        if not all(model_status.values()):
            missing = [k for k, v in model_status.items() if not v]
            logger.error(f"❌ Missing models: {missing}")
            logger.error("Please place models in the models/ directory:")
            logger.error("- models/flux/flux1-schnell.safetensors")
            logger.error("- models/clip/clip_l.safetensors")
            logger.error("- models/clip/t5xxl_fp16.safetensors") 
            logger.error("- models/vae/ae.safetensors")
            return 1
        
        # Load pipeline
        logger.info("\n=== Loading FLUX Pipeline ===")
        
        # Try to get HF token from environment
        import os
        hf_token = os.environ.get('HF_TOKEN')
        if hf_token:
            logger.info("Found HF_TOKEN in environment")
        else:
            logger.warning("No HF_TOKEN found - may need for initial setup")
        
        success = loader.load_pipeline(hf_token)
        
        if not success:
            logger.error("❌ Failed to load FLUX pipeline")
            return 1
        
        # Test generation
        logger.info("\n=== Test Generation ===")
        test_image = loader.generate_coloring_page(
            "simple cartoon dinosaur",
            width=1024,
            height=1024,
            seed=42
        )
        
        if test_image:
            # Save test image
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "server_test.png"
            test_image.save(output_path)
            
            logger.info(f"✅ Test generation successful!")
            logger.info(f"📁 Saved: {output_path}")
        else:
            logger.error("❌ Test generation failed")
            return 1
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 FLUX Coloring Book Generator Ready!")
        logger.info("📍 All systems operational")
        logger.info("🎨 Ready to generate coloring books")
        logger.info("=" * 60)
        
        return 0
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Please install required packages:")
        logger.error("pip install torch diffusers transformers accelerate")
        return 1
    
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main())