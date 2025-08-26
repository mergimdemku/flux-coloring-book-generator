#!/usr/bin/env python3
"""
Create Version 1 Backup of FLUX Coloring Book Project
Includes all essential files for a working deployment
"""

import zipfile
import os
from pathlib import Path
from datetime import datetime

def create_version1_backup():
    """Create comprehensive backup of Version 1"""
    
    print("📦 Creating Version 1 Backup...")
    
    # Core application files (WORKING VERSION)
    core_files = [
        # Main working app
        'coloring_book_app_fixed.py',          # MAIN FIXED APP
        'local_flux_rtx3070.py',               # RTX 3070 optimized FLUX generator
        
        # Startup scripts
        'start_app_fixed.bat',                 # Launch fixed app
        'install_pdf_deps.bat',                # PDF dependencies
        'install_web_deps.bat',                # Web dependencies  
        'test_fixed_app.bat',                  # Test script
        'test_generation.py',                  # Generation test
        
        # Requirements and config
        'requirements_rtx3070.txt',            # RTX 3070 requirements
        'model_config.json',                   # Model configuration
        
        # Documentation
        'FIXED_VERSION_README.md',             # Fixed version docs
        'README.md',                           # Main readme
        'LICENSE',                             # License file
        
        # Core dependencies (fallback versions)
        'coloring_book_app.py',                # Original version (fallback)
        'requirements.txt',                    # General requirements
        
        # Utility scripts
        'fix_pytorch_versions.bat',            # Fix PyTorch versions
        'fix_tokenizer.bat',                   # Fix tokenizer issues
        'check_cuda_support.py',               # CUDA check
        'quick_local_setup.bat',               # Quick setup
    ]
    
    # Source code structure
    src_files = []
    if os.path.exists('src'):
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith(('.py', '.txt', '.md')):
                    rel_path = os.path.relpath(os.path.join(root, file))
                    src_files.append(rel_path)
    
    # Models directory structure
    models_files = []
    if os.path.exists('models'):
        for root, dirs, files in os.walk('models'):
            for file in files:
                if file.endswith(('.py', '.txt', '.md', '.json')):
                    rel_path = os.path.relpath(os.path.join(root, file))
                    models_files.append(rel_path)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"FLUX_Coloring_Book_V1_{timestamp}.zip"
    
    print(f"📦 Creating backup: {backup_filename}")
    
    with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Add core files
        print("\n📁 Adding core application files...")
        for file in core_files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️  {file} (not found)")
        
        # Add source files
        print("\n📁 Adding source code...")
        for file in src_files:
            zipf.write(file)
            print(f"  ✅ {file}")
        
        # Add models structure
        print("\n📁 Adding models structure...")  
        for file in models_files:
            zipf.write(file)
            print(f"  ✅ {file}")
        
        # Add version info
        version_info = f"""
# FLUX Coloring Book Generator - Version 1
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Main Application
- coloring_book_app_fixed.py (PRIMARY)
- local_flux_rtx3070.py (FLUX Generator)

## Startup
- start_app_fixed.bat (MAIN LAUNCHER)
- install_pdf_deps.bat
- test_fixed_app.bat

## Features Working
✅ Scene descriptions properly integrated
✅ Style selection produces different results  
✅ Download buttons fully functional (PNG/PDF/ZIP)
✅ A4 formats (592x840, 840x592) - FLUX compatible
✅ Book generation creates varied content
✅ Proper file management and saving

## Requirements
- Python 3.10+
- RTX 3070 (8GB VRAM) or compatible GPU
- 64GB+ RAM recommended
- Windows 10/11

## Quick Start
1. Extract all files
2. Run: install_pdf_deps.bat
3. Run: start_app_fixed.bat
4. Open: http://localhost:5000
        """
        
        zipf.writestr("VERSION_1_INFO.txt", version_info)
        print(f"  ✅ VERSION_1_INFO.txt")
    
    print(f"\n🎉 Version 1 backup created successfully!")
    print(f"📁 File: {backup_filename}")
    
    # Show file size
    file_size = os.path.getsize(backup_filename) / (1024*1024)
    print(f"📊 Size: {file_size:.1f} MB")
    
    return backup_filename

if __name__ == "__main__":
    backup_file = create_version1_backup()
    
    print(f"\n" + "="*60)
    print("🎯 VERSION 1 BACKUP COMPLETE")
    print("="*60)
    print(f"📦 Backup file: {backup_file}")
    print("🚀 Ready for deployment anywhere!")
    print("="*60)