# 🎨 Coloring Book Generator

An AI-powered desktop application that creates professional coloring books with consistent characters and age-appropriate content.

## Features

### 🧙‍♀️ Wizard-Based Interface
- **Step-by-step guidance** through the entire creation process
- **Project setup** with customizable book details
- **Theme selection** from pre-built story templates or custom stories
- **Real-time preview** and editing capabilities
- **Professional export** in PDF and PNG formats

### 🤖 AI-Powered Generation
- **FLUX-based image generation** optimized for coloring pages
- **Character consistency** across all pages using advanced seed management
- **Age-appropriate complexity** with automatic adjustments for different age ranges
- **Story engine** that creates coherent narratives with proper pacing

### 🎯 Professional Output
- **A4 format** at 300 DPI for print-ready quality
- **Pure black & white** line art perfect for coloring
- **Optimized line thickness** based on target age group
- **PDF export** with proper metadata and structure
- **Quality validation** to ensure coloring suitability

### 👶 Age-Specific Design
- **2-4 years**: Very simple shapes, thick lines, minimal detail
- **3-6 years**: Clear shapes, moderate details, bold outlines  
- **5-8 years**: Detailed scenes, fine outlines, multiple objects
- **6-10 years**: Complex scenes, intricate details, varied line weights

## Installation

### Prerequisites
- **Python 3.8+**
- **CUDA-compatible GPU** (recommended for FLUX generation)
- **8GB+ RAM** (16GB recommended)
- **5GB+ disk space** for models and generated content

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd Kids_App_Painting_Books

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### First Run
On first launch, the application will:
1. Create configuration directories in your home folder
2. Download the FLUX model (may take several minutes)
3. Initialize the generation system

## Usage

### Creating Your First Coloring Book

1. **Launch the application**
   ```bash
   python main.py
   ```

2. **Project Setup**
   - Enter book title (e.g., "Bibo's Adventure")
   - Select target age range
   - Set page count (8-32 pages recommended)
   - Define your main character with detailed description

3. **Choose Theme**
   - Select from pre-built themes (Adventure, Daily Activities, Friendship, etc.)
   - Or provide a custom story outline

4. **Generate & Preview**
   - Click "Generate All Pages" to create images
   - Preview each page and regenerate individual pages if needed
   - Images are automatically processed for optimal coloring

5. **Export**
   - Choose export format (PDF + PNG, PDF only, or PNG only)
   - Select quality level (300 DPI recommended for printing)
   - Export creates print-ready files

### Example Character Descriptions

**Good character descriptions** include specific visual details:
```
"Bibo: small friendly dog with floppy brown ears, round black nose, 
red striped collar with bone-shaped tag, curious expression, 
always wagging tail"
```

**Avoid vague descriptions:**
```
"A cute dog" ❌
```

### Story Themes

#### Adventure Quest
Perfect for stories about finding lost items, exploring new places, or going on journeys.

#### Daily Activities  
Great for routine-based stories: eating, playing, learning, helping with chores.

#### Friendship Journey
Ideal for stories about making friends, helping others, sharing, and cooperation.

#### Learning & Discovery
Educational themes covering school, counting, colors, shapes, and new skills.

#### Seasonal Fun
Holiday activities, weather changes, seasonal foods, and celebrations.

## Technical Details

### Architecture
```
src/
├── core/           # Core application logic
│   ├── app_config.py      # Configuration management
│   └── project_manager.py  # Project lifecycle management
├── ui/             # User interface components
│   ├── main_window.py     # Main application window
│   ├── wizard_pages.py    # Wizard flow pages
│   └── generation_worker.py # Background processing
├── generators/     # Content generation engines
│   ├── story_engine.py    # Story and scene generation
│   ├── prompt_builder.py  # FLUX prompt optimization
│   └── flux_generator.py  # Image generation system
└── utils/          # Utilities and post-processing
    ├── image_processing.py    # Coloring optimization
    ├── pdf_generator.py       # PDF export system
    ├── quality_validator.py   # Quality assurance
    └── character_consistency.py # Character consistency
```

### Generation Pipeline

1. **Story Generation**: Creates coherent narrative scenes
2. **Prompt Building**: Optimizes prompts for FLUX model with character consistency
3. **Image Generation**: Uses FLUX with seed-based consistency
4. **Post-Processing**: Converts to optimal coloring format
5. **Quality Validation**: Ensures suitability for target age
6. **PDF Export**: Creates professional print-ready output

### Character Consistency System

The application maintains character consistency through:
- **Seed-based generation** using deterministic seeds per character
- **Prompt templates** with locked character descriptions
- **Feature locking** for critical character elements (collar, ears, etc.)
- **Validation system** to check consistency across pages

### Quality Assurance

Every generated page is validated for:
- **Line thickness** appropriate for age group
- **Contrast levels** for clear coloring boundaries
- **Color distribution** (proper black/white ratio)
- **Print readiness** (DPI, dimensions, format)
- **Age appropriateness** (complexity, detail level)

## Configuration

### Application Settings
Configuration is stored in `~/ColoringBookGenerator/config.json`:

```json
{
  "image_settings": {
    "width": 2480,
    "height": 3508,
    "dpi": 300
  },
  "generation_settings": {
    "model_name": "flux-schnell",
    "guidance_scale": 7.5,
    "num_inference_steps": 4
  },
  "branding": {
    "company": "3D Gravity Kids",
    "subtitle": "Kopshti Magjik"
  }
}
```

### Memory Requirements
- **FLUX model**: ~2-4GB VRAM
- **Generation**: 1-2GB additional VRAM per image
- **Processing**: 2-4GB RAM for post-processing
- **Storage**: ~50-100MB per completed project

## Troubleshooting

### Common Issues

**"CUDA out of memory"**
- Reduce image dimensions in config
- Use CPU generation (slower but works)
- Close other applications using GPU

**"Generation failed"**
- Check internet connection for first-time model download
- Verify CUDA installation if using GPU
- Try CPU generation as fallback

**"Poor line quality"**
- Adjust post-processing parameters
- Regenerate with different seed
- Check age range settings match desired complexity

**"Character not consistent"**
- Provide more detailed character description
- Use seed-based consistency strategy
- Avoid contradictory character traits

### Performance Optimization

**For faster generation:**
- Use GPU with CUDA support
- Increase VRAM allocation
- Use FLUX-schnell model (4 steps vs 50)
- Generate in batches rather than individually

**For better quality:**
- Use higher DPI settings
- Apply more post-processing steps
- Generate multiple variations and select best

## Development

### Contributing
1. Fork the repository
2. Create feature branch
3. Follow PEP 8 style guidelines
4. Add tests for new functionality
5. Update documentation
6. Submit pull request

### Testing
```bash
# Run basic functionality test
python -c "from src.generators.flux_generator import GenerationManager; print('Import successful')"

# Test image generation
python -c "
from src.generators.flux_generator import GenerationManager, GenerationConfig
config = GenerationConfig()
manager = GenerationManager(config)
print('GPU available:', manager.generator.device if manager.initialize() else 'Failed')
"
```

### Building Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed main.py
```

## License

Copyright © 2025 3D Gravity Kids · Kopshti Magjik

Licensed under the MIT License. See LICENSE file for details.

## Support

For support, feature requests, or bug reports:
- Create an issue in the repository
- Email: support@kopshtimagjik.com
- Website: https://kopshtimagjik.com

---

**Made with ❤️ for creative kids and parents everywhere!**