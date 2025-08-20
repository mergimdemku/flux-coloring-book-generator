"""
Project management system for coloring book projects
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import shutil
import logging

from generators.story_engine import StoryEngine, StoryScene
from generators.prompt_builder import PromptBuilder
from generators.flux_comfyui_generator import FluxComfyUIGenerator, FluxConfig, FluxServerOptimizer
from generators.flux_generator import GenerationManager, GenerationConfig  # Fallback
from utils.image_processing import ColoringBookProcessor
from utils.pdf_generator import PDFGenerator

@dataclass
class ProjectConfig:
    """Configuration for a coloring book project"""
    title: str
    character_name: str
    character_description: str
    age_range: str
    theme: str
    page_count: int
    custom_story: str = ""
    generation_seed: Optional[int] = None

class ProjectManager:
    """Manages coloring book projects from creation to export"""
    
    def __init__(self, app_config):
        self.app_config = app_config
        self.current_project = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize subsystems
        self.story_engine = StoryEngine()
        self.prompt_builder = PromptBuilder()
        self.image_processor = ColoringBookProcessor()
        self.pdf_generator = PDFGenerator()
        
        # Generation manager (initialized when needed)
        self.generation_manager = None
        self.flux_generator = None
        self.current_gpu_config = None  # Store selected GPU config
        
        # GPU manager for dynamic selection
        from utils.gpu_manager import GPUManager
        self.gpu_manager = GPUManager()
    
    def create_project(self, project_config: ProjectConfig) -> str:
        """Create a new coloring book project"""
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())[:8]
        
        # Create project directory
        project_dir = self.app_config.books_dir / f"{project_id}_{self._slugify(project_config.title)}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (project_dir / "images").mkdir(exist_ok=True)
        (project_dir / "processed").mkdir(exist_ok=True)
        (project_dir / "exports").mkdir(exist_ok=True)
        
        # Generate story
        scenes = self.story_engine.generate_story(
            theme=project_config.theme,
            character_name=project_config.character_name,
            character_desc=project_config.character_description,
            page_count=project_config.page_count,
            custom_story=project_config.custom_story
        )
        
        # Create character card for consistency
        character_card = self.prompt_builder.create_character_card(
            project_config.character_name,
            project_config.character_description
        )
        
        # Generate prompts
        prompts = self.prompt_builder.build_batch_prompts(
            scenes=scenes,
            character_card=character_card,
            age_range=project_config.age_range,
            book_title=project_config.title
        )
        
        # Create project metadata
        project_data = {
            'id': project_id,
            'config': asdict(project_config),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'created',
            'project_dir': str(project_dir),
            'scenes': [asdict(scene) for scene in scenes],
            'prompts': prompts,
            'character_card': character_card,
            'generation_status': {
                'completed': False,
                'progress': 0,
                'generated_images': [],
                'failed_images': []
            },
            'export_status': {
                'pdf_exported': False,
                'png_exported': False,
                'export_paths': []
            }
        }
        
        # Save project file
        project_file = project_dir / "project.json"
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        self.current_project = project_data
        self.logger.info(f"Created project: {project_config.title} ({project_id})")
        
        return project_id
    
    def load_project(self, project_path: Path) -> Dict[str, Any]:
        """Load an existing project"""
        
        project_file = project_path / "project.json"
        if not project_file.exists():
            raise FileNotFoundError(f"Project file not found: {project_file}")
        
        with open(project_file, 'r') as f:
            project_data = json.load(f)
        
        self.current_project = project_data
        self.logger.info(f"Loaded project: {project_data['config']['title']}")
        
        return project_data
    
    def save_project(self):
        """Save current project"""
        
        if not self.current_project:
            raise RuntimeError("No current project to save")
        
        project_dir = Path(self.current_project['project_dir'])
        project_file = project_dir / "project.json"
        
        # Update timestamp
        self.current_project['updated_at'] = datetime.now().isoformat()
        
        with open(project_file, 'w') as f:
            json.dump(self.current_project, f, indent=2)
    
    def generate_images(self, progress_callback=None) -> List[Path]:
        """Generate all images for the current project"""
        
        if not self.current_project:
            raise RuntimeError("No current project loaded")
        
        # Initialize FLUX generator if needed
        if not self.flux_generator and not self.generation_manager:
            try:
                # Use selected GPU configuration or get optimal config
                if self.current_gpu_config:
                    self.logger.info(f"Using selected GPU configuration for device {self.current_gpu_config.get('device_id', 0)}")
                    flux_config = self.create_flux_config_from_gpu_selection(self.current_gpu_config)
                else:
                    self.logger.info("No GPU selection, using optimal config...")
                    flux_config = FluxServerOptimizer.get_optimal_config()
                    flux_config.seed = self.current_project['config'].get('generation_seed')
                
                self.flux_generator = FluxComfyUIGenerator(flux_config)
                self.logger.info(f"FLUX generator initialized on {flux_config.device}")
                
            except Exception as e:
                # Fallback to Stable Diffusion
                self.logger.warning(f"FLUX initialization failed, using fallback: {e}")
                gen_config = GenerationConfig(
                    seed=self.current_project['config'].get('generation_seed'),
                    **self.app_config.get('generation_settings', {})
                )
                self.generation_manager = GenerationManager(gen_config)
                
                if not self.generation_manager.initialize():
                    raise RuntimeError("Failed to initialize image generator")
        
        # Get project paths
        project_dir = Path(self.current_project['project_dir'])
        images_dir = project_dir / "images"
        
        # Generate images
        prompts = self.current_project['prompts']
        
        def wrapped_progress(current, total, message):
            if progress_callback:
                progress = int((current / total) * 50)  # First half of progress
                progress_callback(progress, f"Generating: {message}")
            
            # Update project status
            self.current_project['generation_status']['progress'] = current
            
        # Generate images using FLUX or fallback
        if self.flux_generator:
            # Use FLUX batch generation
            self.logger.info("Generating with FLUX...")
            
            # Extract character card and age range from project
            project_data = self.current_project['story_data']
            character_card = f"{project_data['character_name']}: {project_data['character_description']}"
            age_range = project_data['age_range']
            
            # Generate with FLUX
            results = self.flux_generator.generate_story_batch(
                prompts, character_card, age_range, wrapped_progress
            )
            
            # Save images manually
            generated_paths = []
            images_dir.mkdir(parents=True, exist_ok=True)
            
            for i, (image, metadata) in enumerate(results):
                if 'error' not in metadata:
                    page_type = metadata['prompt_data'].get('page_type', 'scene')
                    page_num = metadata['page_number']
                    
                    if page_type == 'cover':
                        filename = f"00_cover.png"
                    elif page_type == 'back_cover':
                        filename = f"99_back_cover.png"
                    elif page_type == 'activity':
                        filename = f"90_activity_{page_num:02d}.png"
                    else:
                        filename = f"{page_num:02d}_scene.png"
                    
                    image_path = images_dir / filename
                    image.save(image_path, 'PNG', dpi=(300, 300))
                    generated_paths.append(image_path)
                    
                    # Save metadata
                    metadata_path = images_dir / f"{filename.stem}_metadata.json"
                    import json
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2, default=str)
        
        else:
            # Fallback to Stable Diffusion
            generated_paths = self.generation_manager.generate_coloring_book(
                prompts=prompts,
                output_dir=images_dir,
                progress_callback=wrapped_progress
            )
        
        # Update project status
        self.current_project['generation_status']['completed'] = True
        self.current_project['generation_status']['generated_images'] = [str(p) for p in generated_paths]
        self.current_project['status'] = 'generated'
        
        self.save_project()
        
        return generated_paths
    
    def process_images(self, progress_callback=None) -> List[Path]:
        """Post-process all generated images"""
        
        if not self.current_project:
            raise RuntimeError("No current project loaded")
        
        project_dir = Path(self.current_project['project_dir'])
        images_dir = project_dir / "images"
        processed_dir = project_dir / "processed"
        
        # Get generated images
        generated_paths = [Path(p) for p in self.current_project['generation_status']['generated_images']]
        
        # Load images
        images = []
        for path in generated_paths:
            if path.exists():
                from PIL import Image
                images.append(Image.open(path))
            else:
                self.logger.warning(f"Generated image not found: {path}")
        
        # Get processing parameters
        age_range = self.current_project['config']['age_range']
        processing_params = self.prompt_builder.get_post_processing_instructions(age_range)
        
        def wrapped_progress(current, total, message):
            if progress_callback:
                progress = 50 + int((current / total) * 30)  # Second portion of progress
                progress_callback(progress, f"Processing: {message}")
        
        # Process images
        processed_images = self.image_processor.batch_process(
            images=images,
            processing_params=processing_params,
            progress_callback=wrapped_progress
        )
        
        # Save processed images
        processed_paths = []
        for i, (processed_img, original_path) in enumerate(zip(processed_images, generated_paths)):
            # Use same filename as original
            processed_path = processed_dir / original_path.name
            processed_img.save(processed_path, 'PNG', dpi=(300, 300))
            processed_paths.append(processed_path)
            
            self.logger.info(f"Processed and saved: {processed_path.name}")
        
        # Update project
        self.current_project['generation_status']['processed_images'] = [str(p) for p in processed_paths]
        self.current_project['status'] = 'processed'
        
        self.save_project()
        
        return processed_paths
    
    def export_pdf(self, include_png: bool = True, progress_callback=None) -> List[Path]:
        """Export project as PDF (and optionally PNG files)"""
        
        if not self.current_project:
            raise RuntimeError("No current project loaded")
        
        project_dir = Path(self.current_project['project_dir'])
        exports_dir = project_dir / "exports"
        
        # Get processed images
        processed_paths = [Path(p) for p in self.current_project['generation_status'].get('processed_images', [])]
        
        if not processed_paths:
            raise RuntimeError("No processed images available. Generate and process images first.")
        
        # Prepare metadata
        config = self.current_project['config']
        metadata = {
            'title': config['title'],
            'character_name': config['character_name'],
            'age_range': config['age_range'],
            'theme': config['theme'],
            'company': self.app_config.get('branding.company', '3D Gravity Kids'),
            'subtitle': self.app_config.get('branding.subtitle', 'Kopshti Magjik'),
            'website': self.app_config.get('branding.website', 'kopshtimagjik.com'),
            'images': processed_paths
        }
        
        exported_paths = []
        
        if progress_callback:
            progress_callback(80, "Creating PDF...")
        
        # Create PDF
        pdf_path = exports_dir / f"{self._slugify(config['title'])}_coloring_book.pdf"
        self.pdf_generator.create_coloring_book(
            images=processed_paths,
            metadata=metadata,
            output_path=pdf_path
        )
        exported_paths.append(pdf_path)
        
        # Copy PNG files if requested
        if include_png:
            if progress_callback:
                progress_callback(90, "Copying PNG files...")
            
            png_dir = exports_dir / "PNG_Files"
            png_dir.mkdir(exist_ok=True)
            
            for processed_path in processed_paths:
                png_export_path = png_dir / processed_path.name
                shutil.copy2(processed_path, png_export_path)
                exported_paths.append(png_export_path)
        
        if progress_callback:
            progress_callback(100, "Export complete!")
        
        # Update project status
        self.current_project['export_status']['pdf_exported'] = True
        self.current_project['export_status']['png_exported'] = include_png
        self.current_project['export_status']['export_paths'] = [str(p) for p in exported_paths]
        self.current_project['status'] = 'exported'
        
        self.save_project()
        
        return exported_paths
    
    def update_gpu_config(self, gpu_config: Dict):
        """Update GPU configuration for generation"""
        self.current_gpu_config = gpu_config
        
        # Clear existing generators to force re-initialization
        if self.flux_generator:
            self.flux_generator.cleanup()
            self.flux_generator = None
        
        if self.generation_manager:
            self.generation_manager.cleanup()
            self.generation_manager = None
        
        self.logger.info(f"Updated GPU config - Device {gpu_config.get('device_id', 0)}: {gpu_config.get('model_variant', 'unknown')}")
    
    def get_available_gpus(self):
        """Get list of available GPUs"""
        return self.gpu_manager.get_available_gpus()
    
    def create_flux_config_from_gpu_selection(self, gpu_config: Dict):
        """Create FluxConfig from GPU selection"""
        from generators.flux_comfyui_generator import FluxConfig
        
        return FluxConfig(
            model_path=gpu_config.get("model_path", "black-forest-labs/FLUX.1-schnell"),
            width=gpu_config.get("width", 512),
            height=gpu_config.get("height", 768),
            num_inference_steps=gpu_config.get("num_inference_steps", 4),
            guidance_scale=gpu_config.get("guidance_scale", 0.0),
            seed=self.current_project['config'].get('generation_seed') if self.current_project else None,
            device=gpu_config.get("device", "cuda:0"),
            dtype=torch.float16,
            use_fp8=gpu_config.get("use_fp8", False),
            enable_cpu_offload=gpu_config.get("enable_cpu_offload", True),
            enable_sequential_cpu_offload=gpu_config.get("enable_sequential_cpu_offload", True)
        )
    
    def regenerate_page(self, page_index: int, progress_callback=None) -> Path:
        """Regenerate a specific page"""
        
        if not self.current_project:
            raise RuntimeError("No current project loaded")
        
        if not self.generation_manager:
            raise RuntimeError("Generation manager not initialized")
        
        prompts = self.current_project['prompts']
        if page_index >= len(prompts):
            raise ValueError(f"Page index {page_index} out of range")
        
        project_dir = Path(self.current_project['project_dir'])
        images_dir = project_dir / "images"
        
        # Generate single image with new seed
        prompt_data = prompts[page_index].copy()
        
        if progress_callback:
            progress_callback(0, f"Regenerating page {page_index + 1}...")
        
        # Use random seed for variation
        import random
        new_seed = random.randint(1, 1000000)
        
        image = self.generation_manager.generator.generate_image(
            prompt=prompt_data['prompt'],
            negative_prompt=prompt_data['negative_prompt'],
            seed=new_seed
        )
        
        # Save image
        page_type = prompt_data.get('page_type', 'scene')
        if page_type == 'cover':
            filename = f"00_cover.png"
        elif page_type == 'back_cover':
            filename = f"99_back_cover.png"
        else:
            filename = f"{page_index:02d}_scene.png"
        
        image_path = images_dir / filename
        image.save(image_path, 'PNG', dpi=(300, 300))
        
        if progress_callback:
            progress_callback(100, f"Page {page_index + 1} regenerated!")
        
        self.logger.info(f"Regenerated page {page_index + 1}: {filename}")
        
        return image_path
    
    def get_project_list(self) -> List[Dict[str, Any]]:
        """Get list of all projects"""
        
        projects = []
        
        for project_dir in self.app_config.books_dir.iterdir():
            if project_dir.is_dir():
                project_file = project_dir / "project.json"
                if project_file.exists():
                    try:
                        with open(project_file, 'r') as f:
                            project_data = json.load(f)
                        
                        projects.append({
                            'id': project_data['id'],
                            'title': project_data['config']['title'],
                            'created_at': project_data['created_at'],
                            'status': project_data['status'],
                            'path': str(project_dir)
                        })
                    except Exception as e:
                        self.logger.error(f"Failed to load project {project_dir}: {e}")
        
        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x['created_at'], reverse=True)
        
        return projects
    
    def delete_project(self, project_path: Path):
        """Delete a project and all its files"""
        
        if project_path.exists():
            shutil.rmtree(project_path)
            self.logger.info(f"Deleted project: {project_path}")
        
        if self.current_project and Path(self.current_project['project_dir']) == project_path:
            self.current_project = None
    
    def _slugify(self, text: str) -> str:
        """Convert text to filename-safe slug"""
        
        import re
        
        # Convert to lowercase and replace spaces with underscores
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '_', slug)
        
        return slug
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Get statistics about current project"""
        
        if not self.current_project:
            return {}
        
        config = self.current_project['config']
        gen_status = self.current_project['generation_status']
        
        stats = {
            'title': config['title'],
            'character': config['character_name'],
            'pages': config['page_count'],
            'theme': config['theme'],
            'age_range': config['age_range'],
            'status': self.current_project['status'],
            'images_generated': len(gen_status.get('generated_images', [])),
            'images_processed': len(gen_status.get('processed_images', [])),
            'generation_progress': gen_status.get('progress', 0)
        }
        
        return stats
    
    def cleanup(self):
        """Cleanup resources"""
        
        if self.generation_manager:
            self.generation_manager.cleanup()
            self.generation_manager = None