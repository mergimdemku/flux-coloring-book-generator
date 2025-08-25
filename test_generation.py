#!/usr/bin/env python3
"""
Simple test to check if FLUX generation is working
"""

import sys
import torch
from local_flux_rtx3070 import FluxRTX3070
from coloring_book_app_fixed import build_enhanced_prompt

def test_generation():
    print("🧪 Testing FLUX Generation...")
    
    # Initialize generator
    generator = FluxRTX3070()
    
    print("\n1. Loading FLUX model...")
    if not generator.load_model():
        print("❌ Failed to load FLUX model")
        return False
    
    print("✅ FLUX model loaded")
    
    # Test enhanced prompt building
    print("\n2. Testing enhanced prompt building...")
    prompt = build_enhanced_prompt("friendly dragon", "flying in clouds", "cartoon", "3-6")
    print(f"Enhanced prompt: {prompt[:100]}...")
    
    # Test generation
    print("\n3. Testing image generation...")
    try:
        image = generator.generate(
            prompt,
            height=595,
            width=842,
            seed=42
        )
        
        if image:
            print("✅ Image generation successful")
            print(f"Image size: {image.size}")
            
            # Save test image
            test_file = "test_generation.png"
            image.save(test_file)
            print(f"✅ Test image saved: {test_file}")
            
            return True
        else:
            print("❌ Image generation returned None")
            return False
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generation()
    if success:
        print("\n🎉 Generation test PASSED")
    else:
        print("\n💥 Generation test FAILED")
    
    sys.exit(0 if success else 1)