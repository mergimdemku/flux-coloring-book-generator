#!/usr/bin/env python3
"""
LOCAL ONLY SERVER - NO DOWNLOADS
Uses only local .safetensors files
"""

import os
import sys
from pathlib import Path

# Disable all HuggingFace downloads
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import logging
import torch
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from models.flux_local_only import FluxLocalOnlyLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Global model loader
model_loader = None

def init_models():
    """Initialize models from local files only"""
    global model_loader
    
    logger.info("=" * 50)
    logger.info("🚀 LOCAL ONLY MODE - NO DOWNLOADS")
    logger.info("=" * 50)
    
    # System info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        logger.info(f"GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        logger.info(f"CUDA: {torch.version.cuda}")
    else:
        logger.warning("No GPU detected - using CPU")
    
    # Initialize loader
    model_loader = FluxLocalOnlyLoader(models_dir="models")
    
    # Check models
    logger.info("\n=== Checking Local Models ===")
    model_status = model_loader.check_models()
    
    if not all(model_status.values()):
        logger.error("\n" + "!" * 50)
        logger.error("MODELS NOT FOUND!")
        logger.error("Please copy your .safetensors files to the models/ directory")
        logger.error("Do NOT run download commands - just copy the files")
        logger.error("!" * 50)
        return False
    
    # Load models
    success = model_loader.load_models()
    
    if success:
        logger.info("\n✅ Local models loaded successfully")
        logger.info("Server ready - NO downloads will occur")
    else:
        logger.error("\n❌ Failed to load local models")
    
    return success

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate coloring page endpoint"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        if not model_loader or not model_loader.loaded:
            return jsonify({'error': 'Models not loaded'}), 500
        
        # For now, just return a message since generation isn't implemented
        return jsonify({
            'status': 'LOCAL_ONLY_MODE',
            'message': 'Generation not yet implemented for pure local mode',
            'prompt': prompt,
            'info': 'This server verifies local models exist but does not download anything'
        })
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get server status"""
    if model_loader:
        return jsonify({
            'status': 'ready',
            'mode': 'LOCAL_ONLY',
            'system': model_loader.get_system_info()
        })
    else:
        return jsonify({
            'status': 'not_initialized',
            'mode': 'LOCAL_ONLY'
        })

if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("🚀 FLUX LOCAL ONLY SERVER")
    logger.info("NO DOWNLOADS - USES ONLY LOCAL .safetensors FILES")
    logger.info("=" * 60)
    
    # Initialize models
    if not init_models():
        logger.error("Failed to initialize. Exiting.")
        sys.exit(1)
    
    # Run server
    logger.info("\n🌐 Starting server on http://0.0.0.0:5000")
    logger.info("This server will NEVER download anything")
    logger.info("It only uses local .safetensors files")
    
    app.run(host='0.0.0.0', port=5000, debug=False)