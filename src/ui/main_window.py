"""
Main application window
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QStackedWidget, QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap

from .wizard_pages import WelcomePage, ProjectSetupPage, ThemeSelectionPage, GenerationPage, ExportPage
from core.app_config import AppConfig

class MainWindow(QMainWindow):
    """Main application window with wizard flow"""
    
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.current_project = None
        
        self.setWindowTitle("Coloring Book Generator - 3D Gravity Kids")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self._create_header(main_layout)
        
        # Content area
        content_frame = QFrame()
        content_frame.setStyleSheet("QFrame { background-color: #f8f9fa; }")
        main_layout.addWidget(content_frame)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Wizard stack
        self.wizard_stack = QStackedWidget()
        content_layout.addWidget(self.wizard_stack)
        
        # Initialize wizard pages
        self._setup_wizard_pages()
        
        # Navigation bar
        self._create_navigation_bar(content_layout)
        
    def _create_header(self, parent_layout):
        """Create application header"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4a90e2, stop: 1 #357abd);
                border: none;
                min-height: 80px;
                max-height: 80px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo/Title
        title_label = QLabel("🎨 Coloring Book Generator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("QLabel { color: white; }")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Branding
        brand_label = QLabel("3D Gravity Kids · Kopshti Magjik")
        brand_font = QFont()
        brand_font.setPointSize(10)
        brand_label.setFont(brand_font)
        brand_label.setStyleSheet("QLabel { color: rgba(255, 255, 255, 0.8); }")
        header_layout.addWidget(brand_label)
        
        parent_layout.addWidget(header)
    
    def _setup_wizard_pages(self):
        """Initialize all wizard pages"""
        self.welcome_page = WelcomePage(self.config)
        self.project_setup_page = ProjectSetupPage(self.config)
        self.theme_page = ThemeSelectionPage(self.config)
        self.generation_page = GenerationPage(self.config)
        self.export_page = ExportPage(self.config)
        
        # Add pages to stack
        self.wizard_stack.addWidget(self.welcome_page)
        self.wizard_stack.addWidget(self.project_setup_page)
        self.wizard_stack.addWidget(self.theme_page)
        self.wizard_stack.addWidget(self.generation_page)
        self.wizard_stack.addWidget(self.export_page)
        
        # Start with welcome page
        self.wizard_stack.setCurrentWidget(self.welcome_page)
        
    def _create_navigation_bar(self, parent_layout):
        """Create navigation bar with next/previous buttons"""
        nav_frame = QFrame()
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-top: 1px solid #dee2e6;
                min-height: 60px;
                max-height: 60px;
            }
        """)
        
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        
        # Previous button
        self.prev_button = QPushButton("← Previous")
        self.prev_button.setMinimumWidth(120)
        self.prev_button.setEnabled(False)
        self.prev_button.setStyleSheet(self._get_button_style())
        nav_layout.addWidget(self.prev_button)
        
        nav_layout.addStretch()
        
        # Page indicator
        self.page_indicator = QLabel("Step 1 of 5")
        self.page_indicator.setStyleSheet("QLabel { color: #6c757d; font-weight: bold; }")
        nav_layout.addWidget(self.page_indicator)
        
        nav_layout.addStretch()
        
        # Next button
        self.next_button = QPushButton("Next →")
        self.next_button.setMinimumWidth(120)
        self.next_button.setStyleSheet(self._get_button_style(primary=True))
        nav_layout.addWidget(self.next_button)
        
        parent_layout.addWidget(nav_frame)
        
    def _get_button_style(self, primary=False):
        """Get button stylesheet"""
        if primary:
            return """
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #545b62;
                }
                QPushButton:pressed {
                    background-color: #3d4144;
                }
                QPushButton:disabled {
                    background-color: #e9ecef;
                    color: #6c757d;
                }
            """
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.next_button.clicked.connect(self._next_page)
        self.prev_button.clicked.connect(self._prev_page)
        
        # Connect wizard page signals
        self.welcome_page.next_requested.connect(self._next_page)
        self.project_setup_page.next_requested.connect(self._next_page)
        self.theme_page.next_requested.connect(self._next_page)
        self.generation_page.next_requested.connect(self._next_page)
        
        # Connect GPU configuration signal
        self.generation_page.gpu_config_changed.connect(self._on_gpu_config_changed)
        
    def _next_page(self):
        """Navigate to next page"""
        current_index = self.wizard_stack.currentIndex()
        if current_index < self.wizard_stack.count() - 1:
            self.wizard_stack.setCurrentIndex(current_index + 1)
            self._update_navigation()
            
    def _prev_page(self):
        """Navigate to previous page"""
        current_index = self.wizard_stack.currentIndex()
        if current_index > 0:
            self.wizard_stack.setCurrentIndex(current_index - 1)
            self._update_navigation()
            
    def _update_navigation(self):
        """Update navigation button states and page indicator"""
        current_index = self.wizard_stack.currentIndex()
        total_pages = self.wizard_stack.count()
        
        # Update buttons
        self.prev_button.setEnabled(current_index > 0)
        self.next_button.setEnabled(current_index < total_pages - 1)
        
        # Update page indicator
        self.page_indicator.setText(f"Step {current_index + 1} of {total_pages}")
        
        # Update next button text for last page
        if current_index == total_pages - 1:
            self.next_button.setText("Finish")
        else:
            self.next_button.setText("Next →")
    
    def _on_gpu_config_changed(self, gpu_config: dict):
        """Handle GPU configuration changes from generation page"""
        # This would connect to project manager if we had it here
        # For now, just log the change
        import logging
        logger = logging.getLogger(__name__)
        
        device_id = gpu_config.get('device_id', 0)
        model_variant = gpu_config.get('model_variant', 'unknown')
        resolution = f"{gpu_config.get('width', 0)}x{gpu_config.get('height', 0)}"
        
        logger.info(f"GPU config updated - Device {device_id}: {model_variant} at {resolution}")
        
        # Store config for when project manager is available
        self.selected_gpu_config = gpu_config