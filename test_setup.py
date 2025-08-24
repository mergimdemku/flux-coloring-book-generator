#!/usr/bin/env python3
"""
Schneller Setup Test für RTX 3070
"""

import sys
import os

def check_python():
    """Check Python version"""
    print("=" * 60)
    print("PYTHON CHECK")
    print("=" * 60)
    
    print(f"Python Version: {sys.version}")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ erforderlich!")
        return False
    else:
        print("✅ Python Version OK")
        return True

def check_gpu():
    """Check GPU availability"""
    print("\n" + "=" * 60)
    print("GPU CHECK")
    print("=" * 60)
    
    try:
        import torch
        
        print(f"PyTorch Version: {torch.__version__}")
        print(f"CUDA verfügbar: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            print(f"GPU: {gpu_name}")
            print(f"VRAM: {vram:.1f}GB")
            
            if "3070" in gpu_name:
                print("✅ RTX 3070 erkannt - perfekt für FLUX!")
                return True
            else:
                print("⚠️ Andere GPU - sollte auch funktionieren")
                return True
        else:
            print("❌ Keine GPU/CUDA gefunden")
            print("Installiere: pip install torch --index-url https://download.pytorch.org/whl/cu121")
            return False
            
    except ImportError:
        print("❌ PyTorch nicht installiert")
        print("Installiere: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        return False

def check_packages():
    """Check required packages"""
    print("\n" + "=" * 60)
    print("PACKAGE CHECK")
    print("=" * 60)
    
    required = {
        'diffusers': 'pip install diffusers',
        'transformers': 'pip install transformers', 
        'accelerate': 'pip install accelerate',
        'PIL': 'pip install pillow',
        'cv2': 'pip install opencv-python',
        'huggingface_hub': 'pip install huggingface-hub'
    }
    
    all_good = True
    
    for package, install_cmd in required.items():
        try:
            if package == 'PIL':
                import PIL
                print(f"✅ {package} (Pillow)")
            elif package == 'cv2':
                import cv2
                print(f"✅ {package} (OpenCV)")
            else:
                __import__(package)
                print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} fehlt")
            print(f"   Install: {install_cmd}")
            all_good = False
    
    return all_good

def check_disk_space():
    """Check available disk space"""
    print("\n" + "=" * 60)
    print("DISK SPACE CHECK")
    print("=" * 60)
    
    import shutil
    
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024**3)
    
    print(f"Freier Speicher: {free_gb:.1f}GB")
    
    if free_gb < 30:
        print("⚠️ Wenig Speicher! FLUX Models brauchen ~25GB")
        return False
    else:
        print("✅ Genug Speicher für FLUX Models")
        return True

def main():
    """Main setup check"""
    print("🚀 FLUX RTX 3070 Setup Check")
    print("Checking system requirements...")
    
    checks = [
        ("Python", check_python()),
        ("GPU/CUDA", check_gpu()),
        ("Packages", check_packages()),
        ("Disk Space", check_disk_space())
    ]
    
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)
    
    all_passed = True
    for name, passed in checks:
        status = "✅ OK" if passed else "❌ Problem"
        print(f"{name:15} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALLES BEREIT FÜR FLUX!")
        print("\nNächste Schritte:")
        print("1. huggingface-cli login")
        print("2. python local_flux_rtx3070.py")
    else:
        print("❌ Setup Probleme gefunden")
        print("Behebe die Probleme oben und führe den Check erneut aus")
    
    print("=" * 60)

if __name__ == "__main__":
    main()