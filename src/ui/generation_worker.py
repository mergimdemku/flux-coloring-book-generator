"""
Background worker threads for image generation and processing
"""

from PySide6.QtCore import QThread, Signal, QObject
from pathlib import Path
from typing import Dict, Any, List
import logging

from core.project_manager import ProjectManager, ProjectConfig

class GenerationWorker(QThread):
    """Background worker for image generation"""
    
    # Signals
    progress_updated = Signal(int, str)  # progress, message
    generation_completed = Signal(list)  # generated image paths
    generation_failed = Signal(str)     # error message
    
    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.project_manager = project_manager
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run image generation in background"""
        try:
            self.progress_updated.emit(0, "Initializing generation...")
            
            # Generate images
            def progress_callback(progress, message):
                self.progress_updated.emit(progress, message)
            
            generated_paths = self.project_manager.generate_images(progress_callback)
            
            self.progress_updated.emit(100, "Generation complete!")
            self.generation_completed.emit(generated_paths)
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            self.generation_failed.emit(str(e))

class ProcessingWorker(QThread):
    """Background worker for image processing"""
    
    # Signals
    progress_updated = Signal(int, str)  # progress, message
    processing_completed = Signal(list)  # processed image paths
    processing_failed = Signal(str)     # error message
    
    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.project_manager = project_manager
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run image processing in background"""
        try:
            self.progress_updated.emit(0, "Starting image processing...")
            
            # Process images
            def progress_callback(progress, message):
                self.progress_updated.emit(progress, message)
            
            processed_paths = self.project_manager.process_images(progress_callback)
            
            self.progress_updated.emit(100, "Processing complete!")
            self.processing_completed.emit(processed_paths)
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            self.processing_failed.emit(str(e))

class ExportWorker(QThread):
    """Background worker for PDF export"""
    
    # Signals
    progress_updated = Signal(int, str)  # progress, message
    export_completed = Signal(list)     # exported file paths
    export_failed = Signal(str)         # error message
    
    def __init__(self, project_manager: ProjectManager, include_png: bool = True):
        super().__init__()
        self.project_manager = project_manager
        self.include_png = include_png
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run export in background"""
        try:
            self.progress_updated.emit(0, "Starting export...")
            
            # Export project
            def progress_callback(progress, message):
                self.progress_updated.emit(progress, message)
            
            exported_paths = self.project_manager.export_pdf(
                include_png=self.include_png,
                progress_callback=progress_callback
            )
            
            self.progress_updated.emit(100, "Export complete!")
            self.export_completed.emit(exported_paths)
            
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            self.export_failed.emit(str(e))

class RegenerateWorker(QThread):
    """Background worker for regenerating single pages"""
    
    # Signals
    progress_updated = Signal(int, str)   # progress, message
    page_regenerated = Signal(int, str)   # page_index, image_path
    regeneration_failed = Signal(str)     # error message
    
    def __init__(self, project_manager: ProjectManager, page_index: int):
        super().__init__()
        self.project_manager = project_manager
        self.page_index = page_index
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run page regeneration in background"""
        try:
            self.progress_updated.emit(0, f"Regenerating page {self.page_index + 1}...")
            
            # Regenerate page
            def progress_callback(progress, message):
                self.progress_updated.emit(progress, message)
            
            image_path = self.project_manager.regenerate_page(
                self.page_index, 
                progress_callback
            )
            
            self.progress_updated.emit(100, "Page regenerated!")
            self.page_regenerated.emit(self.page_index, str(image_path))
            
        except Exception as e:
            self.logger.error(f"Page regeneration failed: {e}")
            self.regeneration_failed.emit(str(e))

class ProjectCreationWorker(QThread):
    """Background worker for creating new projects"""
    
    # Signals
    progress_updated = Signal(int, str)    # progress, message
    project_created = Signal(str, dict)    # project_id, project_data
    creation_failed = Signal(str)          # error message
    
    def __init__(self, project_manager: ProjectManager, project_config: ProjectConfig):
        super().__init__()
        self.project_manager = project_manager
        self.project_config = project_config
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run project creation in background"""
        try:
            self.progress_updated.emit(10, "Creating project structure...")
            
            # Create project
            project_id = self.project_manager.create_project(self.project_config)
            
            self.progress_updated.emit(50, "Generating story...")
            
            # Project is created, get current project data
            project_data = self.project_manager.current_project
            
            self.progress_updated.emit(100, "Project created successfully!")
            self.project_created.emit(project_id, project_data)
            
        except Exception as e:
            self.logger.error(f"Project creation failed: {e}")
            self.creation_failed.emit(str(e))

class WorkerManager(QObject):
    """Manages all background workers"""
    
    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.project_manager = project_manager
        self.logger = logging.getLogger(__name__)
        
        # Current workers
        self.generation_worker = None
        self.processing_worker = None
        self.export_worker = None
        self.regenerate_worker = None
        self.creation_worker = None
    
    def start_generation(self, progress_callback=None, completion_callback=None, error_callback=None):
        """Start image generation in background"""
        
        if self.generation_worker and self.generation_worker.isRunning():
            self.logger.warning("Generation already in progress")
            return
        
        self.generation_worker = GenerationWorker(self.project_manager)
        
        # Connect signals
        if progress_callback:
            self.generation_worker.progress_updated.connect(progress_callback)
        if completion_callback:
            self.generation_worker.generation_completed.connect(completion_callback)
        if error_callback:
            self.generation_worker.generation_failed.connect(error_callback)
        
        # Start worker
        self.generation_worker.start()
    
    def start_processing(self, progress_callback=None, completion_callback=None, error_callback=None):
        """Start image processing in background"""
        
        if self.processing_worker and self.processing_worker.isRunning():
            self.logger.warning("Processing already in progress")
            return
        
        self.processing_worker = ProcessingWorker(self.project_manager)
        
        # Connect signals
        if progress_callback:
            self.processing_worker.progress_updated.connect(progress_callback)
        if completion_callback:
            self.processing_worker.processing_completed.connect(completion_callback)
        if error_callback:
            self.processing_worker.processing_failed.connect(error_callback)
        
        # Start worker
        self.processing_worker.start()
    
    def start_export(self, include_png=True, progress_callback=None, completion_callback=None, error_callback=None):
        """Start export in background"""
        
        if self.export_worker and self.export_worker.isRunning():
            self.logger.warning("Export already in progress")
            return
        
        self.export_worker = ExportWorker(self.project_manager, include_png)
        
        # Connect signals
        if progress_callback:
            self.export_worker.progress_updated.connect(progress_callback)
        if completion_callback:
            self.export_worker.export_completed.connect(completion_callback)
        if error_callback:
            self.export_worker.export_failed.connect(error_callback)
        
        # Start worker
        self.export_worker.start()
    
    def start_page_regeneration(self, page_index, progress_callback=None, completion_callback=None, error_callback=None):
        """Start page regeneration in background"""
        
        if self.regenerate_worker and self.regenerate_worker.isRunning():
            self.logger.warning("Regeneration already in progress")
            return
        
        self.regenerate_worker = RegenerateWorker(self.project_manager, page_index)
        
        # Connect signals
        if progress_callback:
            self.regenerate_worker.progress_updated.connect(progress_callback)
        if completion_callback:
            self.regenerate_worker.page_regenerated.connect(completion_callback)
        if error_callback:
            self.regenerate_worker.regeneration_failed.connect(error_callback)
        
        # Start worker
        self.regenerate_worker.start()
    
    def start_project_creation(self, project_config, progress_callback=None, completion_callback=None, error_callback=None):
        """Start project creation in background"""
        
        if self.creation_worker and self.creation_worker.isRunning():
            self.logger.warning("Project creation already in progress")
            return
        
        self.creation_worker = ProjectCreationWorker(self.project_manager, project_config)
        
        # Connect signals
        if progress_callback:
            self.creation_worker.progress_updated.connect(progress_callback)
        if completion_callback:
            self.creation_worker.project_created.connect(completion_callback)
        if error_callback:
            self.creation_worker.creation_failed.connect(error_callback)
        
        # Start worker
        self.creation_worker.start()
    
    def is_any_worker_running(self) -> bool:
        """Check if any worker is currently running"""
        
        workers = [
            self.generation_worker,
            self.processing_worker,
            self.export_worker,
            self.regenerate_worker,
            self.creation_worker
        ]
        
        return any(worker and worker.isRunning() for worker in workers)
    
    def stop_all_workers(self):
        """Stop all running workers"""
        
        workers = [
            self.generation_worker,
            self.processing_worker,
            self.export_worker,
            self.regenerate_worker,
            self.creation_worker
        ]
        
        for worker in workers:
            if worker and worker.isRunning():
                worker.terminate()
                worker.wait(3000)  # Wait up to 3 seconds
                
        self.logger.info("All workers stopped")