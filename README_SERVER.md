# FLUX Coloring Book Generator - RTX 3070 Server Deployment

## Overview

AI-powered coloring book generator optimized for RTX 3070 (8GB VRAM) deployment. Uses FLUX.1-schnell models adapted from ComfyUI implementation with aggressive memory optimizations for superior image quality and character consistency.

## Features

✨ **FLUX.1-schnell**: Fast 4-step generation optimized for 8GB VRAM
🎯 **RTX 3070 Optimized**: CPU offloading, attention slicing, memory management
🎨 **Character Consistency**: Same character across all story pages
📚 **Complete Books**: Cover, story pages, activities, back cover
🔧 **Docker Ready**: One-command deployment
📊 **Performance Monitoring**: Benchmarks and GPU monitoring
⚡ **Memory Efficient**: Aggressive optimizations for 8GB VRAM constraint

## System Requirements

### Hardware
- **GPU**: RTX 3070 (8GB VRAM) - Primary target
- **GPU Alternative**: RTX 3080/3090 (10-24GB) - Will use higher resolution
- **CPU**: 6+ cores, 12+ threads (important for CPU offloading)
- **RAM**: 16GB+ system RAM (24GB+ recommended for CPU offloading)
- **Storage**: 50GB+ available space (for models and cache)

### Software
- **OS**: Ubuntu 22.04 LTS (recommended) or compatible Linux
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **NVIDIA Container Toolkit**: Latest
- **CUDA**: 12.1+

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd Kids_App_Painting_Books
```

### 2. Check System Requirements

```bash
# Check Docker
docker --version
docker-compose --version

# Check NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi

# Check GPU
nvidia-smi
```

### 3. Deploy

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy the service
./deploy.sh
```

### 4. Verify Deployment

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Check GPU usage
nvidia-smi

# View benchmark results (after first run)
cat benchmark_results.json
```

## Configuration

### Server Configuration (`config.json`)

```json
{
    "server_mode": true,
    "gpu_optimization": {
        "use_fp8": true,
        "memory_fraction": 0.9,
        "enable_xformers": true
    },
    "flux_config": {
        "model": "black-forest-labs/FLUX.1-schnell",
        "steps": 4,
        "guidance": 0.0,
        "resolution": [1024, 1024]
    },
    "cache_settings": {
        "model_cache": "./cache",
        "max_cache_size": "20GB"
    }
}
```

### Environment Variables

```bash
# GPU Configuration
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
TORCH_CUDA_ARCH_LIST=9.0

# Cache Configuration
HF_HOME=/app/cache
TRANSFORMERS_CACHE=/app/cache
DIFFUSERS_CACHE=/app/cache
```

## Performance Optimization

### RTX 3070 Specific Optimizations

1. **Sequential CPU Offload**: Models moved between CPU/GPU as needed
2. **Attention Slicing**: Reduces memory usage during attention computation
3. **VAE Slicing**: Efficient VAE decoding for lower VRAM
4. **xformers**: Memory-efficient attention mechanisms
5. **Aggressive Memory Management**: Cache clearing and tensor management
6. **Smaller Model**: FLUX.1-schnell (4 steps) instead of dev (28 steps)

### Expected Performance (RTX 3070)

- **Single Image**: 8-15 seconds (512x768) with CPU offloading
- **Complete Book**: 8-12 pages in 2-4 minutes
- **Memory Usage**: 6-7.5GB VRAM (with CPU offloading)
- **Throughput**: 4-8 images/minute
- **Model Loading**: ~30-60 seconds initial load with offloading

## Architecture

```
FLUX Coloring Book Generator
├── FLUX Models
│   ├── flux1-dev.safetensors (12GB)
│   ├── clip_l.safetensors (246MB)
│   ├── t5xxl_fp16.safetensors (9.8GB)
│   └── ae.safetensors (335MB)
├── Story Engine
│   ├── Character consistency
│   ├── Age-appropriate content
│   └── Theme variations
├── Image Processing
│   ├── Line art optimization
│   ├── Coloring book preparation
│   └── Quality validation
└── Export System
    ├── PDF generation
    ├── High DPI output
    └── Batch processing
```

## Usage Examples

### Generate Single Book

```bash
# Using server main entry
docker exec flux-coloring-book python3 server_main.py

# Test generation pipeline
docker exec flux-coloring-book python3 -c "
from src.generators.flux_comfyui_generator import FluxComfyUIGenerator, FluxServerOptimizer
config = FluxServerOptimizer.get_optimal_config()
generator = FluxComfyUIGenerator(config)
image = generator.generate_image('simple coloring page of a dog')
image.save('test.png')
print('Generated test image!')
"
```

### Batch Processing

```bash
# Generate multiple books
docker exec flux-coloring-book python3 batch_generate.py \
  --count 10 \
  --theme adventure \
  --age-range "3-6 years"
```

## Monitoring

### GPU Monitoring

```bash
# Real-time GPU usage
watch -n 1 nvidia-smi

# Container resource usage
docker stats flux-coloring-book

# Detailed GPU monitoring (if monitoring service enabled)
curl localhost:9400/metrics | grep nvidia
```

### Application Logs

```bash
# Real-time logs
docker-compose logs -f coloring-book-generator

# Error logs only
docker-compose logs coloring-book-generator | grep ERROR

# Performance logs
docker exec flux-coloring-book tail -f /app/logs/performance.log
```

### Performance Benchmarks

```bash
# View current benchmark
docker exec flux-coloring-book cat benchmark_results.json | jq

# Run new benchmark
docker exec flux-coloring-book python3 -c "
from src.generators.flux_comfyui_generator import FluxComfyUIGenerator, FluxServerOptimizer
config = FluxServerOptimizer.get_optimal_config()
generator = FluxComfyUIGenerator(config)
results = FluxServerOptimizer.benchmark_generation(generator)
print(results)
"
```

## Troubleshooting

### Common Issues

#### GPU Out of Memory
```bash
# Reduce batch size or resolution
docker-compose down
# Edit docker-compose.yml - reduce mem_limit
docker-compose up -d
```

#### Slow Performance
```bash
# Check if FP8 is enabled
docker exec flux-coloring-book python3 -c "
import torch
print('FP8 available:', torch.cuda.get_device_capability()[0] >= 9)
"

# Verify xformers installation
docker exec flux-coloring-book python3 -c "import xformers; print('xformers ok')"
```

#### Model Download Issues
```bash
# Check disk space
df -h

# Clear cache if needed
docker exec flux-coloring-book rm -rf /app/cache/*
docker-compose restart
```

### Log Analysis

```bash
# Check for CUDA errors
docker-compose logs | grep -i cuda

# Check for memory issues
docker-compose logs | grep -i "out of memory\|oom"

# Check model loading
docker-compose logs | grep -i "loading\|model"
```

## Maintenance

### Updates

```bash
# Update application
git pull
docker-compose build --no-cache
docker-compose up -d

# Update models (if needed)
docker exec flux-coloring-book python3 -c "
from diffusers import FluxPipeline
FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-schnell', force_download=True)
"
```

### Backup

```bash
# Backup configuration
tar -czf backup-config.tar.gz config.json docker-compose.yml

# Backup cache (optional - large)
tar -czf backup-cache.tar.gz cache/

# Backup outputs
tar -czf backup-outputs.tar.gz output/
```

### Cleanup

```bash
# Clean Docker
docker system prune -f

# Clean model cache
docker exec flux-coloring-book python3 -c "
import torch
torch.cuda.empty_cache()
"

# Clean old outputs
find output/ -type f -mtime +30 -delete
```

## API Extension

The system can be extended with a REST API:

```python
# server_api.py (future enhancement)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class GenerationRequest(BaseModel):
    character_name: str
    character_description: str
    theme: str
    age_range: str
    pages: int

@app.post("/generate")
async def generate_book(request: GenerationRequest):
    # Implementation here
    pass
```

## Security

- Container runs as non-root user
- No external network access required after setup
- Models cached locally
- Output directory properly isolated

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify GPU status: `nvidia-smi`
3. Check system resources: `htop`, `df -h`
4. Review configuration files

Performance tuning available for specific hardware configurations.