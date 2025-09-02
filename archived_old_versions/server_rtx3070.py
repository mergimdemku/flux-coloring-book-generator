#!/usr/bin/env python3
"""
FLUX SERVER FOR RTX 3070 PC
Access from laptop or any device on your network
"""

import os
import torch
import logging
import json
import io
import base64
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import threading
import queue
import time

# Import our RTX 3070 optimized generator
from local_flux_rtx3070 import FluxRTX3070

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow access from other devices

# Global generator instance
generator = None
generation_queue = queue.Queue()
current_status = {"status": "initializing", "message": "Starting server..."}

class FluxServer:
    """FLUX server optimized for RTX 3070"""
    
    def __init__(self):
        self.generator = FluxRTX3070()
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.generation_history = []
        self.is_generating = False
        
    def initialize(self):
        """Load the model"""
        logger.info("🚀 Initializing FLUX for RTX 3070...")
        success = self.generator.load_model()
        if success:
            logger.info("✅ FLUX ready for generation!")
            return True
        else:
            logger.error("❌ Failed to load FLUX model")
            return False
    
    def generate_image(self, params):
        """Generate an image with given parameters"""
        
        self.is_generating = True
        start_time = time.time()
        
        try:
            # Extract parameters
            prompt = params.get('prompt', 'coloring book page')
            subject = params.get('subject', 'cute dragon')
            age_range = params.get('age_range', '5-8 years')
            resolution = params.get('resolution', 768)
            seed = params.get('seed', -1)
            
            if seed == -1:
                seed = torch.randint(0, 1000000, (1,)).item()
            
            # Build coloring book prompt
            full_prompt = f"""coloring book page of {subject},
            {prompt},
            black and white line art only,
            simple clean outlines,
            no shading, no gray, no color,
            thick black lines on white background,
            suitable for {age_range},
            high contrast line drawing"""
            
            logger.info(f"🎨 Generating: {subject}")
            logger.info(f"Resolution: {resolution}x{resolution}")
            logger.info(f"Seed: {seed}")
            
            # Generate
            image = self.generator.generate(
                full_prompt,
                height=resolution,
                width=resolution,
                seed=seed
            )
            
            if image:
                # Post-process for coloring book
                image = self.generator.optimize_for_coloring(image)
                
                # Save with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"coloring_{timestamp}_{seed}.png"
                filepath = self.output_dir / filename
                image.save(filepath)
                
                # Convert to base64 for web display
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Add to history
                generation_data = {
                    'filename': filename,
                    'prompt': full_prompt,
                    'subject': subject,
                    'seed': seed,
                    'resolution': resolution,
                    'timestamp': timestamp,
                    'generation_time': time.time() - start_time,
                    'image_base64': img_base64
                }
                
                self.generation_history.append(generation_data)
                
                logger.info(f"✅ Generated in {generation_data['generation_time']:.1f}s")
                
                return generation_data
            else:
                return {'error': 'Generation failed'}
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {'error': str(e)}
        finally:
            self.is_generating = False

# Initialize server
server = FluxServer()

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get server status"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        vram_used = torch.cuda.memory_allocated() / (1024**3)
        gpu_info = {
            'name': gpu_name,
            'vram_total': f"{vram_total:.1f}GB",
            'vram_used': f"{vram_used:.1f}GB"
        }
    else:
        gpu_info = {'name': 'No GPU', 'vram_total': '0GB', 'vram_used': '0GB'}
    
    return jsonify({
        'status': 'ready' if server.generator.pipeline else 'not_loaded',
        'gpu': gpu_info,
        'is_generating': server.is_generating,
        'history_count': len(server.generation_history)
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate a coloring page"""
    
    if server.is_generating:
        return jsonify({'error': 'Already generating'}), 429
    
    params = request.json
    result = server.generate_image(params)
    
    if 'error' in result:
        return jsonify(result), 500
    else:
        return jsonify(result)

@app.route('/api/history')
def get_history():
    """Get generation history"""
    # Return last 10 without base64 to save bandwidth
    history = []
    for item in server.generation_history[-10:]:
        h = item.copy()
        h.pop('image_base64', None)  # Remove base64 from list
        history.append(h)
    return jsonify(history)

@app.route('/api/download/<filename>')
def download(filename):
    """Download a generated image"""
    filepath = server.output_dir / filename
    if filepath.exists():
        return send_file(filepath, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    settings_file = Path('server_settings.json')
    
    if request.method == 'POST':
        settings = request.json
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        return jsonify({'status': 'saved'})
    else:
        if settings_file.exists():
            with open(settings_file) as f:
                return jsonify(json.load(f))
        else:
            return jsonify({
                'resolution': 768,
                'age_range': '5-8 years',
                'style': 'simple'
            })

# Create simple HTML template if it doesn't exist
def create_web_interface():
    """Create the web interface HTML"""
    
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>FLUX Coloring Book Generator - RTX 3070 Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .status {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .status-item {
            background: #f0f0f0;
            padding: 10px 20px;
            border-radius: 10px;
        }
        .generator {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .result {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        .result img {
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .info {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: left;
        }
        .download-btn {
            background: #4CAF50;
            color: white;
            padding: 10px 30px;
            border-radius: 10px;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
        }
        .history {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .history-item {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .history-item:hover {
            background: #f0f0f0;
        }
        #loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 FLUX Coloring Book Generator</h1>
            <p>Powered by RTX 3070 Server</p>
            <div class="status" id="status">
                <div class="status-item">Status: <span id="server-status">Checking...</span></div>
                <div class="status-item">GPU: <span id="gpu-info">...</span></div>
                <div class="status-item">VRAM: <span id="vram-info">...</span></div>
            </div>
        </div>

        <div class="generator">
            <h2>Generate Coloring Page</h2>
            <form id="generate-form">
                <div class="form-group">
                    <label>Subject (What to draw)</label>
                    <input type="text" id="subject" placeholder="e.g., friendly dragon, cute cat, spaceship" value="friendly dragon">
                </div>
                
                <div class="form-group">
                    <label>Additional Details (Optional)</label>
                    <textarea id="prompt" rows="3" placeholder="Add more details about the scene...">playing with butterflies in a garden</textarea>
                </div>
                
                <div class="form-group">
                    <label>Age Range</label>
                    <select id="age-range">
                        <option value="3-5 years">3-5 years (Very Simple)</option>
                        <option value="5-8 years" selected>5-8 years (Simple)</option>
                        <option value="8-12 years">8-12 years (Detailed)</option>
                        <option value="12+ years">12+ years (Complex)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Resolution</label>
                    <select id="resolution">
                        <option value="512">512x512 (Fast, Low VRAM)</option>
                        <option value="768" selected>768x768 (Balanced)</option>
                        <option value="1024">1024x1024 (High Quality)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Seed (leave -1 for random)</label>
                    <input type="number" id="seed" value="-1">
                </div>
                
                <button type="submit" class="btn" id="generate-btn">Generate Coloring Page</button>
            </form>
            
            <div id="loading">
                <div class="spinner"></div>
                <p>Generating your coloring page...</p>
            </div>
        </div>

        <div class="result" id="result" style="display: none;">
            <h2>Your Coloring Page</h2>
            <img id="result-image" src="" alt="Generated coloring page">
            <div class="info" id="result-info"></div>
            <a href="#" class="download-btn" id="download-btn" download>Download PNG</a>
        </div>

        <div class="history" id="history" style="display: none;">
            <h2>Recent Generations</h2>
            <div id="history-list"></div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        
        // Check server status
        async function checkStatus() {
            try {
                const response = await fetch(`${API_BASE}/api/status`);
                const data = await response.json();
                
                document.getElementById('server-status').textContent = data.status;
                document.getElementById('gpu-info').textContent = data.gpu.name;
                document.getElementById('vram-info').textContent = `${data.gpu.vram_used} / ${data.gpu.vram_total}`;
                
                if (data.status !== 'ready') {
                    document.getElementById('generate-btn').disabled = true;
                    document.getElementById('generate-btn').textContent = 'Model Loading...';
                } else {
                    document.getElementById('generate-btn').disabled = false;
                    document.getElementById('generate-btn').textContent = 'Generate Coloring Page';
                }
                
                if (data.history_count > 0) {
                    loadHistory();
                }
            } catch (error) {
                console.error('Status check failed:', error);
                document.getElementById('server-status').textContent = 'Error';
            }
        }
        
        // Generate image
        document.getElementById('generate-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('generate-btn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            btn.disabled = true;
            loading.style.display = 'block';
            result.style.display = 'none';
            
            const params = {
                subject: document.getElementById('subject').value,
                prompt: document.getElementById('prompt').value,
                age_range: document.getElementById('age-range').value,
                resolution: parseInt(document.getElementById('resolution').value),
                seed: parseInt(document.getElementById('seed').value)
            };
            
            try {
                const response = await fetch(`${API_BASE}/api/generate`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(params)
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert('Generation failed: ' + data.error);
                } else {
                    // Display result
                    document.getElementById('result-image').src = 'data:image/png;base64,' + data.image_base64;
                    document.getElementById('result-info').innerHTML = `
                        <strong>Subject:</strong> ${data.subject}<br>
                        <strong>Seed:</strong> ${data.seed}<br>
                        <strong>Resolution:</strong> ${data.resolution}x${data.resolution}<br>
                        <strong>Generation Time:</strong> ${data.generation_time.toFixed(1)}s
                    `;
                    document.getElementById('download-btn').href = `/api/download/${data.filename}`;
                    
                    result.style.display = 'block';
                    
                    // Reload history
                    loadHistory();
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
            }
        });
        
        // Load history
        async function loadHistory() {
            try {
                const response = await fetch(`${API_BASE}/api/history`);
                const data = await response.json();
                
                if (data.length > 0) {
                    const historyDiv = document.getElementById('history');
                    const historyList = document.getElementById('history-list');
                    
                    historyList.innerHTML = data.map(item => `
                        <div class="history-item" onclick="window.open('/api/download/${item.filename}')">
                            <strong>${item.subject}</strong> - 
                            ${item.resolution}x${item.resolution} - 
                            Seed: ${item.seed} - 
                            ${item.generation_time.toFixed(1)}s
                        </div>
                    `).join('');
                    
                    historyDiv.style.display = 'block';
                }
            } catch (error) {
                console.error('Failed to load history:', error);
            }
        }
        
        // Check status every 5 seconds
        checkStatus();
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>'''
    
    with open(templates_dir / "index.html", "w") as f:
        f.write(html_content)
    
    logger.info("✅ Created web interface")

def main():
    """Start the FLUX server"""
    
    print("\n" + "="*70)
    print("FLUX COLORING BOOK SERVER - RTX 3070")
    print("="*70)
    
    # Create web interface
    create_web_interface()
    
    # Initialize FLUX
    if not server.initialize():
        print("❌ Failed to initialize FLUX")
        return
    
    # Get local IP
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*70)
    print("🌐 SERVER READY!")
    print("="*70)
    print(f"\n📱 Access from your laptop:")
    print(f"   http://{local_ip}:5000")
    print(f"\n💻 Or locally:")
    print(f"   http://localhost:5000")
    print("\n⚠️  Make sure both devices are on the same network")
    print("📝 Windows Firewall: Allow Python through firewall if prompted")
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()