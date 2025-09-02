#!/usr/bin/env python3
"""
Test just the dependencies without running full pipeline
"""

def test_dependencies():
    """Test all required dependencies"""
    
    print("🧪 Testing Dependencies")
    print("=" * 30)
    
    success = True
    
    # Test 1: NumPy
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
        if np.__version__ >= '2.0':
            print(f"⚠️  Warning: NumPy {np.__version__} may cause PyTorch issues. Recommended: < 2.0")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        success = False
    
    # Test 2: PyTorch
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"✅ VRAM: {vram:.1f}GB")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        success = False
    except Exception as e:
        print(f"⚠️  PyTorch loaded but with issues: {e}")
    
    # Test 3: PIL/Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
        print(f"✅ PIL/Pillow: Available with all features")
    except ImportError as e:
        print(f"❌ PIL/Pillow: {e}")
        success = False
    
    # Test 4: OpenCV
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV: {e}")
        success = False
    
    # Test 5: ReportLab
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        print(f"✅ ReportLab: Available")
    except ImportError as e:
        print(f"❌ ReportLab: {e}")
        success = False
    
    # Test 6: Diffusers
    try:
        from diffusers import FluxPipeline
        print(f"✅ Diffusers: Available")
    except ImportError as e:
        print(f"❌ Diffusers: {e}")
        success = False
    
    # Test 7: Transformers
    try:
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers: {e}")
        success = False
    
    print("\n" + "=" * 30)
    
    if success:
        print("🎉 All dependencies are working!")
        print("\n✅ Ready to test pipeline components")
        return True
    else:
        print("❌ Some dependencies are missing or broken")
        print("\n🔧 Run: fix_all_dependencies.bat")
        return False

def test_simple_components():
    """Test components that don't require FLUX model loading"""
    
    print("\n🧪 Testing Simple Components")
    print("=" * 35)
    
    try:
        # Test story generator (no external deps)
        from kids_story_generator import KidsStoryGenerator
        
        story_gen = KidsStoryGenerator()
        batch = story_gen.get_next_story_batch()
        
        print(f"✅ Story Generator: Working")
        print(f"   Title: {batch['story_data']['title']}")
        print(f"   Style: {batch['story_data']['art_style']['name']}")
        print(f"   Prompts: {len(batch['prompts'])}")
        
    except Exception as e:
        print(f"❌ Story Generator: {e}")
        return False
    
    try:
        # Test PDF generator with dummy data
        from enhanced_pdf_generator import EnhancedPDFGenerator
        from PIL import Image
        
        pdf_gen = EnhancedPDFGenerator("test_output")
        
        # Create dummy images
        cover = Image.new('RGB', (400, 600), color='lightblue')
        pages = [Image.new('RGB', (400, 600), color='white') for _ in range(2)]
        
        test_story = {
            'title': 'Test Story',
            'target_age': '5-8',
            'art_style': {'name': 'Test'},
            'page_count': 2
        }
        
        test_prompts = [
            {'type': 'cover', 'scene_description': 'Test cover'},
            {'type': 'coloring_page', 'scene_description': 'Test page 1'},
            {'type': 'coloring_page', 'scene_description': 'Test page 2'}
        ]
        
        pdf_path = pdf_gen.generate_complete_book_pdf(
            story_data=test_story,
            cover_image=cover,
            coloring_images=pages,
            prompts_data=test_prompts
        )
        
        print(f"✅ PDF Generator: Working")
        print(f"   Created: {pdf_path}")
        
    except Exception as e:
        print(f"❌ PDF Generator: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Simple components are working!")
    return True

def main():
    """Run dependency and simple component tests"""
    
    print("🔧 DEPENDENCY & COMPONENT TEST")
    print("=" * 40)
    
    # Test dependencies first
    deps_ok = test_dependencies()
    
    if deps_ok:
        # Test simple components
        components_ok = test_simple_components()
        
        if components_ok:
            print("\n" + "=" * 40)
            print("✅ READY FOR FLUX MODEL TESTING")
            print("=" * 40)
            print("Next step: python test_complete_pipeline.py")
        else:
            print("\n❌ Component tests failed")
    else:
        print("\n🔧 Fix dependencies first with: fix_all_dependencies.bat")

if __name__ == "__main__":
    main()