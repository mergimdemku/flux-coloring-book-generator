#!/usr/bin/env python3
"""
FLUX COLORING BOOK APP - Web Interface
Professional coloring book generator with RTX 3070
"""

import os
import torch
import logging
import json
import io
import base64
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import time
from local_flux_rtx3070 import FluxRTX3070

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global generator
generator = None
output_dir = Path("generated_books")
output_dir.mkdir(exist_ok=True)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FLUX Coloring Book Studio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .status-bar {
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .status-item {
            background: #f0f0f0;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 0.9em;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 30px;
        }
        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        .control-panel {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            height: fit-content;
        }
        .output-panel {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .btn-secondary {
            background: #6c757d;
            padding: 10px 20px;
            font-size: 14px;
            margin-top: 10px;
        }
        .preview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .preview-card {
            background: #f9f9f9;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s;
        }
        .preview-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .preview-card img {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .preview-info {
            font-size: 0.9em;
            color: #666;
        }
        .progress-bar {
            background: #e0e0e0;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab.active {
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: 600;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .preset-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .preset-btn {
            padding: 10px;
            background: #f0f0f0;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .preset-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        #loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        .spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .download-section {
            background: #f9f9f9;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .download-btn {
            background: #28a745;
            color: white;
            padding: 12px 25px;
            border-radius: 10px;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            transition: all 0.3s;
        }
        .download-btn:hover {
            background: #218838;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 FLUX Coloring Book Studio</h1>
            <p>Professional AI-Powered Coloring Book Generator</p>
            <div class="status-bar">
                <div class="status-item">GPU: <span id="gpu-name">RTX 3070</span></div>
                <div class="status-item">VRAM: <span id="vram-usage">0GB / 8GB</span></div>
                <div class="status-item">Status: <span id="system-status">Ready</span></div>
                <div class="status-item">Generated: <span id="total-generated">0</span> images</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="control-panel">
                <h2>Generate Coloring Pages</h2>
                
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('single')">Single Page</div>
                    <div class="tab" onclick="switchTab('book')">Complete Book</div>
                    <div class="tab" onclick="switchTab('batch')">Batch Mode</div>
                </div>

                <div id="single-tab" class="tab-content active">
                    <div class="form-group">
                        <label>Subject/Character</label>
                        <input type="text" id="subject" placeholder="e.g., friendly dragon, cute cat" value="friendly dragon">
                    </div>
                    
                    <div class="form-group">
                        <label>Scene Description</label>
                        <textarea id="scene" rows="3" placeholder="Describe the scene...">playing with butterflies in a magical garden</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Quick Presets</label>
                        <div class="preset-buttons">
                            <button class="preset-btn" onclick="setPreset('dragon')">🐉 Dragon</button>
                            <button class="preset-btn" onclick="setPreset('unicorn')">🦄 Unicorn</button>
                            <button class="preset-btn" onclick="setPreset('dinosaur')">🦕 Dinosaur</button>
                            <button class="preset-btn" onclick="setPreset('robot')">🤖 Robot</button>
                            <button class="preset-btn" onclick="setPreset('princess')">👸 Princess</button>
                            <button class="preset-btn" onclick="setPreset('pirate')">🏴‍☠️ Pirate</button>
                            <button class="preset-btn" onclick="setPreset('space')">🚀 Space</button>
                            <button class="preset-btn" onclick="setPreset('ocean')">🌊 Ocean</button>
                        </div>
                    </div>
                </div>

                <div id="book-tab" class="tab-content">
                    <div class="form-group">
                        <label>Book Theme</label>
                        <input type="text" id="book-theme" placeholder="e.g., Adventures of Dragon" value="Adventures of Friendly Dragon">
                    </div>
                    
                    <div class="form-group">
                        <label>Number of Pages</label>
                        <select id="num-pages">
                            <option value="5">5 Pages (Quick)</option>
                            <option value="10" selected>10 Pages (Standard)</option>
                            <option value="15">15 Pages (Extended)</option>
                            <option value="20">20 Pages (Full Book)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Book Type</label>
                        <select id="book-type">
                            <option value="story">Story Book</option>
                            <option value="alphabet">Alphabet Book</option>
                            <option value="numbers">Numbers Book</option>
                            <option value="animals">Animal Book</option>
                            <option value="vehicles">Vehicle Book</option>
                        </select>
                    </div>
                </div>

                <div id="batch-tab" class="tab-content">
                    <div class="form-group">
                        <label>Batch Prompts (one per line)</label>
                        <textarea id="batch-prompts" rows="8" placeholder="cute cat playing with yarn
friendly dog in the park
happy elephant spraying water
...">cute cat playing with yarn
friendly dog in the park
happy elephant spraying water
silly monkey eating banana
brave lion roaring</textarea>
                    </div>
                </div>

                <div class="form-group">
                    <label>Age Range</label>
                    <select id="age-range">
                        <option value="2-4">2-4 years (Very Simple)</option>
                        <option value="3-6" selected>3-6 years (Simple)</option>
                        <option value="5-8">5-8 years (Moderate)</option>
                        <option value="7-10">7-10 years (Detailed)</option>
                        <option value="10+">10+ years (Complex)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Style</label>
                    <select id="style">
                        <option value="simple">Simple Lines</option>
                        <option value="cartoon" selected>Cartoon Style</option>
                        <option value="realistic">Realistic</option>
                        <option value="mandala">Mandala Style</option>
                        <option value="kawaii">Kawaii/Cute</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Resolution</label>
                    <select id="resolution">
                        <option value="512">512x512 (Fast, Draft)</option>
                        <option value="768" selected>768x768 (Balanced)</option>
                        <option value="1024">1024x1024 (High Quality)</option>
                    </select>
                </div>

                <button class="btn" onclick="generate()" id="generate-btn">
                    🎨 Generate Coloring Page
                </button>
                
                <button class="btn btn-secondary" onclick="clearAll()">
                    Clear All
                </button>
            </div>

            <div class="output-panel">
                <h2>Generated Coloring Pages</h2>
                
                <div id="loading">
                    <div class="spinner"></div>
                    <p>Creating your coloring page...</p>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress">0%</div>
                    </div>
                </div>

                <div id="preview-section">
                    <div class="preview-grid" id="preview-grid">
                        <!-- Generated images will appear here -->
                    </div>
                </div>

                <div class="download-section" id="download-section" style="display: none;">
                    <h3>📥 Download Options</h3>
                    <a href="#" class="download-btn" id="download-single">Download Image</a>
                    <a href="#" class="download-btn" id="download-pdf">Download as PDF</a>
                    <a href="#" class="download-btn" id="download-all">Download All (ZIP)</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'single';
        let generatedImages = [];
        let isGenerating = false;

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
            
            // Update button text
            const btn = document.getElementById('generate-btn');
            if (tab === 'single') {
                btn.textContent = '🎨 Generate Coloring Page';
            } else if (tab === 'book') {
                btn.textContent = '📚 Generate Complete Book';
            } else {
                btn.textContent = '🎨 Generate Batch';
            }
        }

        function setPreset(preset) {
            const presets = {
                dragon: { subject: 'friendly dragon', scene: 'flying through clouds with a rainbow' },
                unicorn: { subject: 'magical unicorn', scene: 'in an enchanted forest with flowers' },
                dinosaur: { subject: 'happy dinosaur', scene: 'playing in prehistoric jungle' },
                robot: { subject: 'cute robot', scene: 'building toys in a workshop' },
                princess: { subject: 'princess', scene: 'in castle garden with butterflies' },
                pirate: { subject: 'pirate', scene: 'on ship searching for treasure' },
                space: { subject: 'astronaut', scene: 'exploring alien planet with stars' },
                ocean: { subject: 'mermaid', scene: 'swimming with dolphins and fish' }
            };
            
            if (presets[preset]) {
                document.getElementById('subject').value = presets[preset].subject;
                document.getElementById('scene').value = presets[preset].scene;
            }
        }

        async function generate() {
            if (isGenerating) return;
            
            isGenerating = true;
            const btn = document.getElementById('generate-btn');
            btn.disabled = true;
            
            document.getElementById('loading').style.display = 'block';
            updateProgress(0);
            
            let params = {
                age_range: document.getElementById('age-range').value,
                style: document.getElementById('style').value,
                resolution: parseInt(document.getElementById('resolution').value)
            };
            
            if (currentTab === 'single') {
                params.mode = 'single';
                params.subject = document.getElementById('subject').value;
                params.scene = document.getElementById('scene').value;
            } else if (currentTab === 'book') {
                params.mode = 'book';
                params.theme = document.getElementById('book-theme').value;
                params.num_pages = parseInt(document.getElementById('num-pages').value);
                params.book_type = document.getElementById('book-type').value;
            } else {
                params.mode = 'batch';
                params.prompts = document.getElementById('batch-prompts').value.split('\\n').filter(p => p.trim());
            }
            
            try {
                // Simulate progress
                for (let i = 0; i <= 90; i += 10) {
                    updateProgress(i);
                    await new Promise(r => setTimeout(r, 200));
                }
                
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                
                const result = await response.json();
                updateProgress(100);
                
                if (result.success) {
                    displayResults(result.images);
                    updateStats();
                } else {
                    alert('Generation failed: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                isGenerating = false;
                btn.disabled = false;
                document.getElementById('loading').style.display = 'none';
            }
        }

        function updateProgress(percent) {
            const progressBar = document.getElementById('progress');
            progressBar.style.width = percent + '%';
            progressBar.textContent = percent + '%';
        }

        function displayResults(images) {
            const grid = document.getElementById('preview-grid');
            
            images.forEach((img, index) => {
                const card = document.createElement('div');
                card.className = 'preview-card';
                card.innerHTML = `
                    <img src="data:image/png;base64,${img.base64}" alt="Coloring page ${index + 1}">
                    <div class="preview-info">
                        Page ${index + 1}
                        <br>
                        <small>${img.prompt || ''}</small>
                    </div>
                `;
                grid.appendChild(card);
                generatedImages.push(img);
            });
            
            document.getElementById('download-section').style.display = 'block';
            document.getElementById('total-generated').textContent = generatedImages.length;
        }

        function clearAll() {
            document.getElementById('preview-grid').innerHTML = '';
            generatedImages = [];
            document.getElementById('download-section').style.display = 'none';
        }

        async function updateStats() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                document.getElementById('gpu-name').textContent = status.gpu;
                document.getElementById('vram-usage').textContent = status.vram;
                document.getElementById('system-status').textContent = status.status;
            } catch (error) {
                console.error('Failed to update stats:', error);
            }
        }

        // Update stats every 5 seconds
        setInterval(updateStats, 5000);
        updateStats();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    """Get system status"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_used = torch.cuda.memory_allocated() / (1024**3)
        vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        vram_info = f"{vram_used:.1f}GB / {vram_total:.1f}GB"
    else:
        gpu_name = "No GPU"
        vram_info = "N/A"
    
    return jsonify({
        'gpu': gpu_name,
        'vram': vram_info,
        'status': 'Ready' if generator else 'Loading...'
    })

@app.route('/api/generate', methods=['POST'])
def generate_api():
    """Generate coloring pages"""
    global generator
    
    if not generator:
        return jsonify({'success': False, 'error': 'Generator not loaded'})
    
    params = request.json
    mode = params.get('mode', 'single')
    
    try:
        images = []
        
        if mode == 'single':
            # Generate single image
            subject = params.get('subject', 'dragon')
            scene = params.get('scene', '')
            prompt = f"{subject} {scene}"
            
            image = generator.generate_coloring_page(subject, params.get('age_range', '3-6'))
            
            if image:
                # Convert to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = output_dir / f"coloring_{timestamp}.png"
                image.save(filename)
                
                images.append({
                    'base64': img_base64,
                    'prompt': prompt,
                    'filename': str(filename)
                })
        
        elif mode == 'book':
            # Generate complete book
            theme = params.get('theme', 'Dragon Adventures')
            num_pages = params.get('num_pages', 10)
            
            # Generate pages
            for i in range(num_pages):
                prompt = f"{theme} - Page {i+1}"
                image = generator.generate_coloring_page(prompt, params.get('age_range', '3-6'))
                
                if image:
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    images.append({
                        'base64': img_base64,
                        'prompt': prompt
                    })
        
        elif mode == 'batch':
            # Batch generation
            prompts = params.get('prompts', [])
            
            for prompt in prompts[:10]:  # Limit to 10
                if prompt.strip():
                    image = generator.generate_coloring_page(prompt.strip(), params.get('age_range', '3-6'))
                    
                    if image:
                        buffered = io.BytesIO()
                        image.save(buffered, format="PNG")
                        img_base64 = base64.b64encode(buffered.getvalue()).decode()
                        
                        images.append({
                            'base64': img_base64,
                            'prompt': prompt
                        })
        
        return jsonify({
            'success': True,
            'images': images
        })
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

def main():
    """Start the app"""
    global generator
    
    print("\n" + "="*70)
    print("🎨 FLUX COLORING BOOK STUDIO")
    print("="*70)
    
    # Initialize generator
    print("\nLoading FLUX model...")
    generator = FluxRTX3070()
    
    if generator.load_model():
        print("✅ FLUX loaded successfully!")
    else:
        print("❌ Failed to load FLUX")
        return
    
    print("\n" + "="*70)
    print("🌐 Starting Web Server")
    print("="*70)
    print("\n📱 Open in browser:")
    print("   http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    print("="*70)
    
    # Start server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()