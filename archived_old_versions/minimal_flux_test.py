#!/usr/bin/env python3
"""
Minimaler FLUX Test - nur das Nötigste
"""

import torch
import gc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_imports():
    """Test basic imports"""
    print("=" * 60)
    print("BASIC IMPORTS TEST")
    print("=" * 60)
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"✅ CUDA: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            print(f"✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB")
    except Exception as e:
        print(f"❌ PyTorch: {e}")
        return False
    
    try:
        import diffusers
        print(f"✅ diffusers {diffusers.__version__}")
    except Exception as e:
        print(f"❌ diffusers: {e}")
        return False
    
    try:
        import transformers
        print(f"✅ transformers {transformers.__version__}")
    except Exception as e:
        print(f"❌ transformers: {e}")
        return False
    
    return True

def test_flux_import():
    """Test FLUX pipeline import"""
    print("\n" + "=" * 60)
    print("FLUX PIPELINE TEST")
    print("=" * 60)
    
    try:
        from diffusers import FluxPipeline
        print("✅ FluxPipeline import erfolreich")
        return True
    except Exception as e:
        print(f"❌ FluxPipeline import fehler: {e}")
        return False

def test_simple_tensor():
    """Test basic CUDA operations"""
    print("\n" + "=" * 60)
    print("CUDA OPERATIONS TEST")
    print("=" * 60)
    
    if not torch.cuda.is_available():
        print("❌ CUDA nicht verfügbar")
        return False
    
    try:
        # Simple tensor operation
        device = "cuda"
        x = torch.randn(1000, 1000, device=device)
        y = torch.randn(1000, 1000, device=device)
        z = torch.mm(x, y)
        
        print(f"✅ CUDA Matrix Multiplikation: {z.shape}")
        print(f"✅ VRAM verwendet: {torch.cuda.memory_allocated() / (1024**2):.1f}MB")
        
        # Cleanup
        del x, y, z
        torch.cuda.empty_cache()
        
        return True
    except Exception as e:
        print(f"❌ CUDA Operations: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 MINIMAL FLUX TEST")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("FLUX Import", test_flux_import),
        ("CUDA Operations", test_simple_tensor)
    ]
    
    all_passed = True
    for name, test_func in tests:
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALLE TESTS BESTANDEN!")
        print("Bereit für FLUX Generation!")
        
        # Quick generation test
        print("\n" + "=" * 60)
        print("SCHNELLER FLUX TEST")
        print("=" * 60)
        
        try:
            from diffusers import FluxPipeline
            print("Lade FLUX Pipeline (das kann dauern beim ersten Mal)...")
            
            pipe = FluxPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-schnell",
                torch_dtype=torch.float16,
                cache_dir="./cache"
            )
            
            # Move to GPU
            pipe = pipe.to("cuda")
            
            # Enable optimizations
            pipe.enable_model_cpu_offload()
            
            print("✅ FLUX geladen!")
            print("🎨 Teste Generation...")
            
            # Simple generation
            image = pipe(
                "simple coloring book page of a cat",
                num_inference_steps=4,
                guidance_scale=0.0,
                height=512,
                width=512
            ).images[0]
            
            # Save
            image.save("test_generation.png")
            print("✅ Test Bild gespeichert: test_generation.png")
            print("🎉 FLUX FUNKTIONIERT!")
            
        except Exception as e:
            print(f"❌ FLUX Test fehlgeschlagen: {e}")
            print("Führe zuerst fix_pytorch_versions.bat aus")
    else:
        print("❌ Tests fehlgeschlagen")
        print("Führe fix_pytorch_versions.bat aus")

if __name__ == "__main__":
    main()