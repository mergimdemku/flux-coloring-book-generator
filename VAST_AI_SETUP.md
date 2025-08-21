# 🚀 Vast.ai RTX 5090 Deployment Guide

## Step-by-Step Setup

### 1. **Launch Vast.ai Instance**

#### Recommended Configuration:
- **GPU**: RTX 5090 (32GB VRAM)
- **CPU**: 8+ cores
- **RAM**: 32GB+
- **Storage**: 150GB+ (for models and cache)
- **Image**: `pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel`
- **Docker**: Enabled
- **Ports**: 8080 (optional, for web interface)

#### Launch Command:
```bash
# Search for RTX 5090 instances
vastai search offers 'gpu_name=RTX_5090'

# Rent instance (replace INSTANCE_ID with actual ID)
vastai create instance INSTANCE_ID \
  --image pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel \
  --disk 150 \
  --args '-p 8080:8080'
```

### 2. **Connect to Instance**

```bash
# Get connection info
vastai show instances

# SSH into your instance (replace with your details)
ssh root@ssh.vast.ai -p YOUR_PORT
```

### 3. **Deploy Application**

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Kids_App_Painting_Books.git
cd Kids_App_Painting_Books

# Run deployment script
chmod +x vast_ai_deploy.sh
./vast_ai_deploy.sh
```

### 4. **Monitor Deployment**

The script will:
- ✅ Detect RTX 5090 and configure optimally
- ✅ Install Docker and NVIDIA Container Toolkit
- ✅ Download FLUX models (~22GB)
- ✅ Start the application
- ✅ Create monitoring tools

## 📊 **What You'll Get:**

### **RTX 5090 Performance:**
- **Model**: FLUX.1-dev (highest quality)
- **Resolution**: 1024×1024
- **Steps**: 28 (maximum quality)
- **Batch Size**: 8 images simultaneously
- **FP8 Precision**: Enabled
- **Speed**: 1-3 seconds per image

### **Expected Costs:**
- **RTX 5090**: ~$1.50-3.00/hour on vast.ai
- **Complete book generation**: ~$0.10-0.20 per book
- **Model downloads**: One-time (cached afterward)

## 🔧 **Management Commands:**

After deployment, you'll have these tools:

```bash
# Monitor GPU and performance
./monitor_gpu.sh

# View application logs
./view_logs.sh

# Restart application
./restart_app.sh

# Stop application (save money)
docker-compose down

# Start application
docker-compose up -d
```

## 📁 **File Locations:**

```bash
/opt/flux-coloring-book/
├── output/          # Generated coloring books
├── cache/           # Downloaded models (~22GB)
├── logs/            # Application logs
├── config.json      # RTX 5090 optimized settings
└── monitor_gpu.sh   # GPU monitoring tool
```

## 🔍 **Verify Installation:**

```bash
# Check GPU
nvidia-smi

# Check application status
docker-compose ps

# Test generation (after models download)
python3 server_main.py
```

## 💡 **Cost Optimization Tips:**

1. **Stop when not using**: `docker-compose down`
2. **Use spot instances**: Lower cost, may be interrupted
3. **Batch your work**: Generate multiple books in one session
4. **Monitor usage**: Use `./monitor_gpu.sh` to track efficiency

## 🚨 **Troubleshooting:**

### **If deployment fails:**
```bash
# Check logs
./view_logs.sh

# Restart deployment
./restart_app.sh

# Manual restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **If models don't download:**
```bash
# Check internet connection
curl -I https://huggingface.co

# Check disk space
df -h

# Clear cache and retry
rm -rf cache/*
docker-compose restart
```

### **If generation is slow:**
```bash
# Check GPU usage
./monitor_gpu.sh

# Verify RTX 5090 optimizations
cat config.json | grep -A 10 "gpu_optimization"
```

## 🌐 **Remote Access:**

### **Option 1: Command Line**
```bash
# SSH into vast.ai instance
ssh root@ssh.vast.ai -p YOUR_PORT

# Run generation
cd /opt/flux-coloring-book
python3 server_main.py
```

### **Option 2: Web Interface** (Future)
```bash
# If web interface is added later
http://YOUR_INSTANCE_IP:8080
```

### **Option 3: File Transfer**
```bash
# Download generated books
scp -P YOUR_PORT root@ssh.vast.ai:/opt/flux-coloring-book/output/* ./local_folder/

# Upload custom prompts
scp -P YOUR_PORT ./my_prompts.json root@ssh.vast.ai:/opt/flux-coloring-book/
```

## 🎯 **Next Steps After Deployment:**

1. **Wait for model download** (~10-20 minutes)
2. **Run test generation** to verify setup
3. **Generate your first coloring book**
4. **Monitor performance** with included tools
5. **Scale usage** based on your needs

Your RTX 5090 FLUX generator will be ready to create premium quality coloring books! 🎨