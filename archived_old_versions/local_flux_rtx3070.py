#!/usr/bin/env python3
"""
FLUX FOR RTX 3070 - Optimized for 8GB VRAM + 128GB RAM
Local development version with aggressive optimizations
"""

import torch
import gc
import os
from pathlib import Path
import logging
import json
from PIL import Image
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FluxRTX3070:
    """FLUX optimized for RTX 3070 with 8GB VRAM"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16
        
        # Print system info
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"GPU: {gpu_name} ({vram:.1f}GB VRAM)")
            
            # RTX 3070 should have ~8GB
            if vram < 10:
                logger.info("✅ RTX 3070 detected - Using optimized settings")
                self.resolution = 768  # Safe for 8GB
                self.enable_cpu_offload = True
            else:
                self.resolution = 1024
                self.enable_cpu_offload = False
        else:
            logger.warning("No GPU detected - using CPU (will be slow)")
            self.resolution = 512
            self.dtype = torch.float32
        
        # Check RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            logger.info(f"RAM: {ram_gb:.1f}GB")
            if ram_gb > 64:
                logger.info("✅ High RAM detected - Can use aggressive CPU offloading")
        except:
            pass
        
        self.pipeline = None
    
    def load_model(self, model_path=None):
        """Load FLUX with RTX 3070 optimizations"""
        
        logger.info("\n🔧 Loading FLUX for RTX 3070...")
        
        try:
            from diffusers import FluxPipeline
            
            # Clear memory before loading
            gc.collect()
            torch.cuda.empty_cache()
            
            if model_path and Path(model_path).exists():
                logger.info(f"Loading from local path: {model_path}")
                self.pipeline = FluxPipeline.from_pretrained(
                    model_path,
                    torch_dtype=self.dtype,
                    local_files_only=True
                )
            else:
                logger.info("Loading from HuggingFace...")
                self.pipeline = FluxPipeline.from_pretrained(
                    "black-forest-labs/FLUX.1-schnell",
                    torch_dtype=self.dtype,
                    cache_dir="./cache"
                )
            
            # RTX 3070 Optimizations
            logger.info("\n⚙️ Applying RTX 3070 optimizations...")
            
            # 1. Enable CPU offloading (crucial for 8GB VRAM)
            if self.enable_cpu_offload:
                self.pipeline.enable_model_cpu_offload()
                logger.info("✅ CPU offloading enabled (saves VRAM)")
            
            # 2. Enable xformers if available (saves ~2GB VRAM)
            try:
                self.pipeline.enable_xformers_memory_efficient_attention()
                logger.info("✅ xformers enabled (saves ~2GB VRAM)")
            except:
                logger.info("⚠️ xformers not available - install with: pip install xformers")
            
            # 3. Enable attention slicing (saves VRAM)
            self.pipeline.enable_attention_slicing("auto")
            logger.info("✅ Attention slicing enabled")
            
            # 4. Enable VAE slicing (saves VRAM during decode)
            if hasattr(self.pipeline.vae, 'enable_slicing'):
                self.pipeline.vae.enable_slicing()
                logger.info("✅ VAE slicing enabled")
            
            # 5. Move to device if not using CPU offload
            if not self.enable_cpu_offload:
                self.pipeline = self.pipeline.to(self.device)
            
            logger.info("\n✅ FLUX loaded and optimized for RTX 3070!")
            
            # Memory report
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / (1024**3)
                reserved = torch.cuda.memory_reserved() / (1024**3)
                logger.info(f"VRAM: {allocated:.1f}GB allocated, {reserved:.1f}GB reserved")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def generate(self, prompt, **kwargs):
        """Generate image with RTX 3070 safe settings"""
        
        if not self.pipeline:
            logger.error("Model not loaded! Call load_model() first")
            return None
        
        # Default settings optimized for RTX 3070
        settings = {
            "prompt": prompt,
            "num_inference_steps": 4,  # schnell optimal
            "guidance_scale": 0.0,     # schnell doesn't use CFG
            "height": kwargs.get("height", self.resolution),
            "width": kwargs.get("width", self.resolution),
            "generator": torch.Generator(device="cpu").manual_seed(
                kwargs.get("seed", 42)
            )
        }
        
        logger.info(f"\n🎨 Generating {settings['width']}x{settings['height']}...")
        logger.info(f"Prompt: {prompt[:100]}...")
        
        # Clear cache before generation
        gc.collect()
        torch.cuda.empty_cache()
        
        try:
            start_time = time.time()
            
            # Generate with autocast for mixed precision
            with torch.cuda.amp.autocast(enabled=(self.device == "cuda")):
                result = self.pipeline(**settings)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Generated in {elapsed:.1f} seconds")
            
            # Memory usage after generation
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / (1024**3)
                logger.info(f"VRAM used: {allocated:.1f}GB")
            
            return result.images[0]
            
        except torch.cuda.OutOfMemoryError:
            logger.error("❌ Out of VRAM! Trying smaller resolution...")
            
            # Retry with smaller resolution
            if settings['height'] > 512:
                logger.info("Retrying at 512x512...")
                settings['height'] = 512
                settings['width'] = 512
                
                gc.collect()
                torch.cuda.empty_cache()
                
                with torch.cuda.amp.autocast(enabled=(self.device == "cuda")):
                    result = self.pipeline(**settings)
                
                logger.info("✅ Generated at reduced resolution")
                return result.images[0]
            else:
                logger.error("Still OOM at 512x512 - need more optimization")
                return None
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def generate_coloring_page(self, subject, age_range="5-8 years"):
        """Generate a coloring book page"""
        
        # Build optimized prompt for coloring books
        prompt = f"""coloring book page of {subject}, 
        black and white line art only, 
        simple clean outlines, 
        no shading, no gray, no color,
        thick black lines on white background,
        suitable for {age_range},
        high contrast line drawing"""
        
        image = self.generate(prompt)
        
        if image:
            # Post-process for better coloring book style
            image = self.optimize_for_coloring(image)
        
        return image
    
    def optimize_for_coloring(self, image):
        """Convert to pure black and white line art"""
        
        import cv2
        import numpy as np
        
        # Convert to numpy
        img = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to get pure black and white
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find edges for cleaner lines
        edges = cv2.Canny(thresh, 50, 150)
        
        # Invert (we want black lines on white)
        result = 255 - edges
        
        # Convert back to PIL Image
        return Image.fromarray(result)

def main():
    """Test the RTX 3070 optimized FLUX"""
    
    print("\n" + "="*70)
    print("FLUX COLORING BOOK GENERATOR - RTX 3070 Edition")
    print("="*70)
    
    # Load config if exists
    if Path("rtx3070_config.json").exists():
        with open("rtx3070_config.json") as f:
            config = json.load(f)
        print(f"\n✅ Loaded config: {config}")
    
    # Initialize generator
    generator = FluxRTX3070()
    
    # Load model
    if generator.load_model():
        
        # Test generation
        print("\n" + "="*70)
        print("GENERATING TEST COLORING PAGE")
        print("="*70)
        
        image = generator.generate_coloring_page(
            subject="a friendly dragon playing with butterflies",
            age_range="5-8 years"
        )
        
        if image:
            output_path = "coloring_page_rtx3070.png"
            image.save(output_path)
            print(f"\n✅ Saved: {output_path}")
            print(f"Size: {image.size}")
        else:
            print("\n❌ Generation failed")
    else:
        print("\n❌ Failed to load model")
        print("\n📝 Make sure to:")
        print("1. Install requirements: pip install -r requirements.txt")
        print("2. Login to HuggingFace: huggingface-cli login")
        print("3. Have ~25GB free space for model download")

if __name__ == "__main__":
    main()