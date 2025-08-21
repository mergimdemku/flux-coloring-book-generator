"""
Wizard pages for the coloring book generation process
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QSpinBox, QComboBox, QPushButton,
                               QTextEdit, QGroupBox, QRadioButton, QButtonGroup,
                               QScrollArea, QGridLayout, QProgressBar, QListWidget,
                               QListWidgetItem, QFrame)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QPixmap

from core.app_config import AppConfig

class BasePage(QWidget):
    """Base class for wizard pages"""
    
    next_requested = Signal()
    
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface - override in subclasses"""
        pass
    
    def validate(self) -> bool:
        """Validate page input - override in subclasses"""
        return True
    
    def get_data(self) -> dict:
        """Get page data - override in subclasses"""
        return {}

class WelcomePage(BasePage):
    """Welcome page with app introduction"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # Welcome title
        title = QLabel("Welcome to Coloring Book Generator!")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("QLabel { color: #2c3e50; margin: 20px; }")
        layout.addWidget(title)
        
        # Description
        description = QLabel("""
        Create beautiful, printable coloring books with AI-generated content.
        
        Features:
        • Consistent character throughout the book
        • Age-appropriate themes and complexity
        • High-quality line art perfect for coloring
        • Professional PDF output ready for printing
        • Multiple export formats (PNG, PDF)
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("""
            QLabel { 
                color: #34495e; 
                font-size: 14px; 
                line-height: 1.6;
                margin: 20px;
                max-width: 500px;
            }
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Start button
        start_button = QPushButton("Get Started")
        start_button.setMinimumSize(200, 50)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        start_button.clicked.connect(self.next_requested.emit)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

class ProjectSetupPage(BasePage):
    """Project setup page for basic book configuration"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Project Setup")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("QLabel { color: #2c3e50; margin-bottom: 10px; }")
        layout.addWidget(title)
        
        # Book details group
        book_group = QGroupBox("Book Details")
        book_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        book_layout = QVBoxLayout(book_group)
        
        # Title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Book Title:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Bibo's Adventure")
        title_layout.addWidget(self.title_input)
        book_layout.addLayout(title_layout)
        
        # Age range
        age_layout = QHBoxLayout()
        age_layout.addWidget(QLabel("Target Age Range:"))
        self.age_combo = QComboBox()
        self.age_combo.addItems([
            "2-4 years (Simple shapes)",
            "3-6 years (Medium complexity)", 
            "5-8 years (More details)",
            "6-10 years (Complex scenes)"
        ])
        self.age_combo.setCurrentIndex(1)  # Default to 3-6
        age_layout.addWidget(self.age_combo)
        book_layout.addLayout(age_layout)
        
        # Page count
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Total Pages:"))
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(8, 32)
        self.pages_spin.setValue(24)
        self.pages_spin.setSuffix(" pages")
        pages_layout.addWidget(self.pages_spin)
        pages_layout.addWidget(QLabel("(includes cover, scenes, and activities)"))
        pages_layout.addStretch()
        book_layout.addLayout(pages_layout)
        
        layout.addWidget(book_group)
        
        # Character details group
        char_group = QGroupBox("Main Character")
        char_layout = QVBoxLayout(char_group)
        
        # Character name
        char_name_layout = QHBoxLayout()
        char_name_layout.addWidget(QLabel("Character Name:"))
        self.char_name_input = QLineEdit()
        self.char_name_input.setPlaceholderText("e.g., Bibo")
        char_name_layout.addWidget(self.char_name_input)
        char_layout.addLayout(char_name_layout)
        
        # Character description
        char_desc_layout = QVBoxLayout()
        char_desc_layout.addWidget(QLabel("Character Description:"))
        self.char_desc_input = QTextEdit()
        self.char_desc_input.setPlaceholderText("Describe your character's appearance: small dog, floppy ears, striped collar...")
        self.char_desc_input.setMaximumHeight(80)
        char_desc_layout.addWidget(self.char_desc_input)
        char_layout.addLayout(char_desc_layout)
        
        layout.addWidget(char_group)
        
        layout.addStretch()
        
    def validate(self) -> bool:
        """Validate page input"""
        return (len(self.title_input.text().strip()) > 0 and 
                len(self.char_name_input.text().strip()) > 0)
    
    def get_data(self) -> dict:
        """Get page data"""
        return {
            'title': self.title_input.text().strip(),
            'age_range': self.age_combo.currentText(),
            'page_count': self.pages_spin.value(),
            'character_name': self.char_name_input.text().strip(),
            'character_description': self.char_desc_input.toPlainText().strip()
        }

class ThemeSelectionPage(BasePage):
    """Theme selection page"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Choose Theme & Story")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("QLabel { color: #2c3e50; margin-bottom: 10px; }")
        layout.addWidget(title)
        
        # Theme selection
        theme_group = QGroupBox("Story Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_buttons = QButtonGroup()
        
        themes = [
            ("Adventure Quest", "Finding something lost, exploring new places"),
            ("Daily Activities", "Eating, playing, sleeping, household tasks"),
            ("Friendship Journey", "Making friends, helping others, sharing"),
            ("Learning & Discovery", "School, counting, colors, shapes"),
            ("Seasonal Fun", "Holiday activities, weather, nature changes"),
            ("Custom Story", "I'll provide my own story outline")
        ]
        
        for i, (theme_name, description) in enumerate(themes):
            radio = QRadioButton(f"{theme_name}: {description}")
            radio.setStyleSheet("QRadioButton { font-size: 13px; padding: 8px; }")
            if i == 0:  # Default selection
                radio.setChecked(True)
            self.theme_buttons.addButton(radio, i)
            theme_layout.addWidget(radio)
        
        layout.addWidget(theme_group)
        
        # Custom story input (initially hidden)
        self.custom_story_group = QGroupBox("Custom Story Outline")
        custom_layout = QVBoxLayout(self.custom_story_group)
        
        custom_layout.addWidget(QLabel("Describe your story (optional - AI will expand):"))
        self.custom_story_input = QTextEdit()
        self.custom_story_input.setPlaceholderText("e.g., A dog searches for food and learns about helping others...")
        self.custom_story_input.setMaximumHeight(100)
        custom_layout.addWidget(self.custom_story_input)
        
        self.custom_story_group.setVisible(False)
        layout.addWidget(self.custom_story_group)
        
        # Connect theme selection to show/hide custom input
        self.theme_buttons.buttonToggled.connect(self._on_theme_changed)
        
        layout.addStretch()
    
    def _on_theme_changed(self, button, checked):
        """Handle theme selection change"""
        if checked and self.theme_buttons.id(button) == 5:  # Custom story
            self.custom_story_group.setVisible(True)
        else:
            self.custom_story_group.setVisible(False)
    
    def get_data(self) -> dict:
        """Get page data"""
        selected_id = self.theme_buttons.checkedId()
        themes = ["adventure", "daily", "friendship", "learning", "seasonal", "custom"]
        
        data = {
            'theme': themes[selected_id] if selected_id >= 0 else themes[0],
            'custom_story': self.custom_story_input.toPlainText().strip() if selected_id == 5 else ""
        }
        return data

class GenerationPage(BasePage):
    """Generation page with GPU selection, preview and editing"""
    
    # Signal for GPU configuration changes
    gpu_config_changed = Signal(dict)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Generate & Preview")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("QLabel { color: #2c3e50; margin-bottom: 10px; }")
        layout.addWidget(title)
        
        # GPU Selection Section
        from ui.gpu_selection_widget import GPUSelectionWidget
        self.gpu_widget = GPUSelectionWidget()
        self.gpu_widget.gpu_selected.connect(self.on_gpu_config_changed)
        layout.addWidget(self.gpu_widget)
        
        # Generation controls
        controls_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("Generate All Pages")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        controls_layout.addWidget(self.generate_button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Preview area
        preview_group = QGroupBox("Page Preview & Editing")
        preview_layout = QVBoxLayout(preview_group)
        
        # Page selector
        page_controls = QHBoxLayout()
        page_controls.addWidget(QLabel("Page:"))
        
        self.page_list = QComboBox()
        self.page_list.addItem("Generate pages first...")
        self.page_list.setEnabled(False)
        page_controls.addWidget(self.page_list)
        
        self.regenerate_button = QPushButton("Regenerate This Page")
        self.regenerate_button.setEnabled(False)
        page_controls.addWidget(self.regenerate_button)
        
        page_controls.addStretch()
        preview_layout.addLayout(page_controls)
        
        # Preview image area
        scroll = QScrollArea()
        self.preview_label = QLabel("Click 'Generate All Pages' to start...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 500)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                background-color: #ecf0f1;
                color: #7f8c8d;
                font-size: 16px;
            }
        """)
        scroll.setWidget(self.preview_label)
        scroll.setWidgetResizable(True)
        preview_layout.addWidget(scroll)
        
        layout.addWidget(preview_group)
    
    def on_gpu_config_changed(self, device_id: int, config: dict):
        """Handle GPU configuration changes"""
        self.gpu_config_changed.emit(config)
        
        # Update generation button text with GPU info
        gpu_info = self.gpu_widget.get_selected_gpu_info()
        if gpu_info:
            gpu_name = gpu_info.name.replace("NVIDIA GeForce ", "").replace("RTX ", "RTX")
            self.generate_button.setText(f"Generate with {gpu_name}")
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"GPU config changed - Device {device_id}: {config.get('width')}x{config.get('height')}, {config.get('model_variant')}")
    
    def get_data(self) -> dict:
        """Get generation page data including GPU config"""
        base_data = super().get_data()
        
        # Add GPU configuration
        if hasattr(self, 'gpu_widget'):
            gpu_config = self.gpu_widget.get_current_config()
            gpu_info = self.gpu_widget.get_selected_gpu_info()
            
            base_data.update({
                'gpu_config': gpu_config,
                'selected_gpu': {
                    'device_id': gpu_info.device_id if gpu_info else 0,
                    'name': gpu_info.name if gpu_info else "Unknown",
                    'memory_gb': gpu_info.memory_gb if gpu_info else 0,
                    'type': gpu_info.gpu_type.value if gpu_info else "unknown"
                } if gpu_info else None
            })
        
        return base_data
    
    def validate(self) -> bool:
        """Validate GPU selection and configuration"""
        if not hasattr(self, 'gpu_widget'):
            return True
            
        gpu_info = self.gpu_widget.get_selected_gpu_info()
        if not gpu_info:
            return False
            
        config = self.gpu_widget.get_current_config()
        
        # Basic validation
        if config.get('width', 0) < 256 or config.get('height', 0) < 256:
            return False
            
        if config.get('num_inference_steps', 0) < 1:
            return False
        
        return True

class ExportPage(BasePage):
    """Export page for final output"""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Page title
        title = QLabel("Export Your Coloring Book")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("QLabel { color: #2c3e50; margin-bottom: 10px; }")
        layout.addWidget(title)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF + PNG Files", "PDF Only", "PNG Files Only"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # Quality selection
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High (300 DPI)", "Medium (150 DPI)", "Low (72 DPI)"])
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        options_layout.addLayout(quality_layout)
        
        layout.addWidget(options_group)
        
        # Export button
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("Export Coloring Book")
        self.export_button.setMinimumSize(200, 50)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        export_layout.addWidget(self.export_button)
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        # Export progress
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        layout.addWidget(self.export_progress)
        
        # Results area
        self.results_label = QLabel("")
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("QLabel { color: #27ae60; font-weight: bold; }")
        layout.addWidget(self.results_label)
        
        layout.addStretch()
        
    def get_data(self) -> dict:
        """Get export settings"""
        return {
            'format': self.format_combo.currentText(),
            'quality': self.quality_combo.currentText()
        }