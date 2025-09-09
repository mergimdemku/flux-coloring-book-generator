# 🎨 AI-Powered Children's Coloring Book Generator

## 📖 Overview

An automated system that generates unique children's coloring books using AI (FLUX.1-schnell). Creates simple, single-theme coloring books with clean line art, automatically processes them into PDFs, and ensures no repetition of themes or content.

## ✨ Key Features

- **🎯 Single Theme Focus**: Each book has one clear theme (dogs, dinosaurs, kitchen, etc.)
- **🚫 No Text Artifacts**: Optimized prompts eliminate text/letters in images
- **♾️ Infinite Variety**: 30+ themes with automatic uniqueness tracking
- **🤖 Fully Automated**: Generates books every 10 minutes, processes every 5 minutes
- **📄 PDF Generation**: Complete coloring books with covers and 12 pages
- **🔄 No Duplicates**: Checks existing stories to prevent repetition

## 🚀 Quick Start

### One-Click Start (Windows)
```batch
start_coloring_book_system.bat
```

### Manual Start
```bash
# Start continuous author (generates every 10 minutes)
python3 core_system/simple_theme_author.py continuous 10

# In another terminal, start pipeline (processes every 5 minutes)
python3 core_system/automated_monitor_pipeline.py
```

### Single Generation Test
```bash
# Generate one book
python3 core_system/simple_theme_author.py
```

## 📁 System Architecture

```
flux-coloring-book-generator/
├── core_system/
│   ├── simple_theme_author.py        # Generates themed coloring books
│   ├── optimized_flux_generator.py   # FLUX AI image generation
│   ├── automated_monitor_pipeline.py # Processes books to PDFs
│   ├── enhanced_pdf_generator.py     # Creates PDF files
│   └── model_config.py              # Model configuration
├── new_stories/                     # Generated book JSONs (input)
├── old_stories/                     # Processed book JSONs (archive)
├── automated_books/                 # Final PDF coloring books (output)
├── generated_books/
│   └── used_themes.json            # Tracks used themes
└── start_coloring_book_system.bat  # One-click startup
```

## 🎨 Available Themes (30+)

### Animals
- `dogs` - 15 breeds (Husky, Labrador, Golden Retriever...)
- `cats` - 12 breeds (Persian, Siamese, Maine Coon...)
- `farm_animals` - Cow, Pig, Horse, Chicken...
- `ocean_animals` - Dolphin, Whale, Shark, Octopus...
- `birds` - Eagle, Parrot, Owl, Peacock...
- `dinosaurs` - T-Rex, Triceratops, Stegosaurus...

### Nature & Food
- `flowers` - Sunflower, Rose, Tulip, Daisy...
- `trees` - Oak, Pine, Apple, Cherry...
- `fruits` - Apple, Banana, Orange, Strawberry...
- `vegetables` - Carrot, Tomato, Potato...
- `desserts` - Ice cream, Cake, Cookie...
- `mexican_food` - Taco, Burrito, Quesadilla...
- `japanese_food` - Sushi, Ramen, Tempura...

### Home & Vehicles
- `kitchen` - Refrigerator, Oven, Microwave...
- `bedroom` - Bed, Pillow, Blanket...
- `bathroom` - Bathtub, Shower, Toilet...
- `cars` - Race car, Police car, Fire truck...
- `trains` - Steam train, Bullet train...
- `airplanes` - Passenger plane, Fighter jet...

### Sports & Space
- `sports_balls` - Soccer, Basketball, Football...
- `space` - Moon, Sun, Earth, Mars...

### Seasons
- `summer` - Beach, Sandcastle, Ice cream...
- `winter` - Snowman, Snowflake, Ski...

### Special Characters
- `the_dog_benji` - "Dog Benji swimming", "Dog Benji eating"...
- `princess_lily` - "Princess Lily dancing", "Princess Lily in castle"...
- `world_cultures` - Japanese kimono, Mexican sombrero...

## 🔧 How It Works

### 1. Simple Theme Author
- Selects unused theme from database
- Generates 12 unique prompts (1 cover + 11 pages)
- Saves JSON to `new_stories/` folder
- Tracks used themes to prevent repetition
- Runs every 10 minutes automatically

### 2. Automated Monitor Pipeline
- Monitors `new_stories/` folder every 5 minutes
- Loads JSON story files
- Generates images using FLUX.1-schnell
- Creates PDF with cover and coloring pages
- Moves processed stories to `old_stories/`

### 3. FLUX Image Generator
- Uses optimized prompts (77 token limit)
- Prioritizes "no text" keywords in first 30 tokens
- Generates clean black & white line art
- 592x832 resolution for coloring pages

## 📝 Generated Output Format

### Story JSON Structure
```json
{
  "story": {
    "title": "Dogs Coloring Book ABC12345",
    "theme": "dogs",
    "theme_title": "Dogs",
    "total_pages": 12,
    "prompts": [
      {
        "type": "cover",
        "character": "Dogs collection",
        "scene": "Husky, Labrador, Beagle, Poodle together",
        "negative": "text, words, letters..."
      },
      {
        "type": "coloring_page",
        "page_number": 1,
        "character": "Husky",
        "scene": "Husky playing in park"
      }
    ]
  }
}
```

## 🛠️ Configuration

### Change Generation Interval
```python
# In simple_theme_author.py
run_continuous_author(interval_minutes=10)  # Change to desired minutes
```

### Change Processing Interval
```python
# In automated_monitor_pipeline.py
self.check_interval = 300  # Change to seconds (300 = 5 minutes)
```

### Add New Themes
Edit `simple_theme_author.py`:
```python
"my_new_theme": {
    "title": "My New Theme",
    "items": ["Item 1", "Item 2", "Item 3"...]
}
```

## 🔍 Monitoring & Logs

### Check Generated Books
```bash
ls new_stories/*.json
```

### Check Completed PDFs
```bash
ls automated_books/*.pdf
```

### View Used Themes
```bash
cat generated_books/used_themes.json
```

## ⚠️ Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- 8GB+ VRAM for FLUX model
- Dependencies: torch, diffusers, Pillow, reportlab

## 🐛 Troubleshooting

### Images Have Text Artifacts
- Fixed in `optimized_flux_generator.py`
- "no text" keywords in first 30 tokens

### Duplicate Books Generated
- System checks `new_stories/` and `old_stories/`
- Tracks themes in `used_themes.json`

### Pipeline Not Processing
- Check `new_stories/` has JSON files
- Verify FLUX model loaded correctly
- Check GPU memory availability

## 📊 System Statistics

- **Generation Speed**: ~30 seconds per book structure
- **Processing Speed**: ~2-3 minutes per complete PDF
- **Available Themes**: 30+ unique themes
- **Pages per Book**: 12 (1 cover + 11 content)
- **Image Resolution**: 592x832 pixels
- **Check Intervals**: Author 10 min, Pipeline 5 min

## 🎯 Production Ready

This system is production-ready with:
- ✅ Automatic continuous generation
- ✅ Duplicate prevention
- ✅ Error handling and recovery
- ✅ Clean, maintainable code
- ✅ Comprehensive logging
- ✅ One-click startup

## 📜 License

Private Repository - All Rights Reserved

## 👨‍💻 Author

Developed with Claude AI assistance for automated children's content generation.

---

**Last Updated**: January 8, 2025  
**Version**: 2.0 - Complete System Overhaul  
**Status**: ✅ Production Ready
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