#!/usr/bin/env python3
"""
Switch pipeline to use optimized generator with cached models
"""

import os
import shutil
from pathlib import Path

def switch_to_optimized():
    """Switch the pipeline to use optimized generator"""
    
    print("🔄 Switching to optimized FLUX generator...")
    
    # Backup the current pipeline
    pipeline_path = Path("core_system/automated_monitor_pipeline.py")
    backup_path = Path("core_system/automated_monitor_pipeline.py.backup")
    
    if pipeline_path.exists():
        shutil.copy2(pipeline_path, backup_path)
        print(f"✅ Backed up current pipeline to {backup_path}")
    
    # Read current pipeline
    with open(pipeline_path, 'r') as f:
        content = f.read()
    
    # Replace imports and class usage
    content = content.replace(
        'from clean_line_flux_generator import CleanLineFluxGenerator',
        'from optimized_flux_generator import OptimizedFluxGenerator'
    )
    
    content = content.replace(
        'CleanLineFluxGenerator()',
        'OptimizedFluxGenerator()'
    )
    
    content = content.replace(
        'self.generator = CleanLineFluxGenerator()',
        'self.generator = OptimizedFluxGenerator()'
    )
    
    # Write updated pipeline
    with open(pipeline_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated pipeline to use OptimizedFluxGenerator")
    print("✅ Will use your cached models - no download needed")
    print("✅ Better quality expected (CLIP token optimization)")
    print()
    print("🎯 Now you can run:")
    print("   python core_system/automated_monitor_pipeline.py")
    print()
    print("📁 Your model cache:")
    print("   Kids_Coloring_Books/flux-coloring-book-generator/cache/models--black-forest-labs--FLUX.1-schnell")

if __name__ == "__main__":
    switch_to_optimized()