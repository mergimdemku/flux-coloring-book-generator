#!/bin/bash
# FLUX Coloring Book Generator - Server Deployment Script
# Optimized for RTX 5090

set -e

echo "🚀 FLUX Coloring Book Generator - RTX 3070 Deployment"
echo "======================================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Don't run as root - Docker should be configured for non-root access"
    exit 1
fi

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Check NVIDIA Docker runtime
if ! docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA Docker runtime not working. Please install nvidia-container-toolkit."
    exit 1
fi

echo "✅ Docker and NVIDIA runtime ready"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output cache models logs

# Set permissions
chmod 755 output cache models logs

# Check available GPU memory
echo "🎮 Checking GPU specifications..."
GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits)
echo "GPU: $GPU_INFO"

# Check GPU type and optimize accordingly
if echo "$GPU_INFO" | grep -i "3070" > /dev/null; then
    echo "🎯 RTX 3070 detected! Using 8GB VRAM optimizations."
    export RTX_3070=true
    export GPU_MEMORY="8GB"
elif echo "$GPU_INFO" | grep -i "3080" > /dev/null; then
    echo "🚀 RTX 3080 detected! Using 10/12GB optimizations."
    export RTX_3070=false
    export GPU_MEMORY="10GB+"
elif echo "$GPU_INFO" | grep -i "4090\|5090" > /dev/null; then
    echo "⚡ RTX 4090/5090 detected! Using high-end optimizations."
    export RTX_3070=false
    export GPU_MEMORY="24GB+"
else
    echo "⚠️  GPU not specifically optimized for. Using RTX 3070 settings."
    export RTX_3070=true
    export GPU_MEMORY="Unknown"
fi

# Build the container
echo "🏗️  Building FLUX Coloring Book Generator container..."
docker-compose build --no-cache

# Pull any missing base images
echo "📦 Ensuring all dependencies are available..."
docker-compose pull

# Create initial configuration
echo "⚙️  Creating server configuration..."

# Set resolution based on GPU memory
if [ "$RTX_3070" = true ]; then
    RESOLUTION="[512, 768]"
    CACHE_SIZE="10GB"
    MEMORY_FRACTION="0.85"
else
    RESOLUTION="[768, 768]"
    CACHE_SIZE="15GB"
    MEMORY_FRACTION="0.9"
fi

cat > config.json <<EOF
{
    "server_mode": true,
    "gpu_optimization": {
        "use_fp8": false,
        "memory_fraction": ${MEMORY_FRACTION},
        "enable_xformers": true,
        "enable_cpu_offload": ${RTX_3070},
        "enable_attention_slicing": true,
        "enable_vae_slicing": true
    },
    "flux_config": {
        "model": "black-forest-labs/FLUX.1-schnell",
        "steps": 4,
        "guidance": 0.0,
        "resolution": ${RESOLUTION},
        "enable_sequential_cpu_offload": ${RTX_3070}
    },
    "cache_settings": {
        "model_cache": "./cache",
        "max_cache_size": "${CACHE_SIZE}",
        "gpu_memory": "${GPU_MEMORY}"
    },
    "output_settings": {
        "output_dir": "./output",
        "dpi": 300,
        "format": "PNG"
    }
}
EOF

echo "✅ Configuration created"

# Start the services
echo "🚀 Starting FLUX Coloring Book Generator..."
docker-compose up -d

# Wait for startup
echo "⏳ Waiting for service to initialize..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Service is running!"
    
    # Show service status
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    
    echo ""
    echo "📝 Logs (last 20 lines):"
    docker-compose logs --tail=20
    
    echo ""
    echo "🎉 FLUX Coloring Book Generator is now running!"
    echo ""
    echo "📍 Service Details:"
    echo "   • Container: flux-coloring-book"
    echo "   • Output Directory: $(pwd)/output"
    echo "   • Cache Directory: $(pwd)/cache"
    echo "   • Log Directory: $(pwd)/logs"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • View logs:    docker-compose logs -f"
    echo "   • Stop service: docker-compose down"
    echo "   • Restart:      docker-compose restart"
    echo "   • Update:       git pull && docker-compose build && docker-compose up -d"
    echo ""
    echo "📈 Monitoring:"
    echo "   • GPU usage:    nvidia-smi"
    echo "   • Container:    docker stats flux-coloring-book"
    
    # Show benchmark if available
    if docker exec flux-coloring-book test -f /app/benchmark_results.json 2>/dev/null; then
        echo ""
        echo "⚡ Performance Benchmark:"
        docker exec flux-coloring-book cat /app/benchmark_results.json | jq '.single_image_time, .avg_image_time, .vram_used_gb' 2>/dev/null || echo "   (Benchmark will be available after first run)"
    fi
    
    echo ""
    echo "✨ Ready to generate coloring books!"
    
else
    echo "❌ Service failed to start properly"
    echo "📝 Recent logs:"
    docker-compose logs --tail=50
    exit 1
fi