"""
GPU Selection Widget for the Generation Step
Allows users to choose which GPU to use and see optimization settings
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QPushButton, QProgressBar, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFrame, QGridLayout,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QIcon, QPalette
from typing import List, Dict, Optional
import logging

from utils.gpu_manager import GPUManager, GPUInfo, GPUType

class GPUBenchmarkWorker(QThread):
    """Background worker for GPU benchmarking"""
    
    benchmark_completed = Signal(int, dict)  # device_id, results
    benchmark_failed = Signal(int, str)      # device_id, error
    
    def __init__(self, gpu_manager: GPUManager, device_id: int):
        super().__init__()
        self.gpu_manager = gpu_manager
        self.device_id = device_id
    
    def run(self):
        try:
            gpu_info = self.gpu_manager.get_gpu_by_id(self.device_id)
            if gpu_info:
                results = self.gpu_manager.benchmark_gpu(gpu_info)
                self.benchmark_completed.emit(self.device_id, results)
            else:
                self.benchmark_failed.emit(self.device_id, "GPU not found")
        except Exception as e:
            self.benchmark_failed.emit(self.device_id, str(e))

class GPUSelectionWidget(QWidget):
    """Widget for selecting and configuring GPU for generation"""
    
    # Signals
    gpu_selected = Signal(int, dict)  # device_id, config
    benchmark_requested = Signal(int)  # device_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        self.gpu_manager = GPUManager()
        self.available_gpus = self.gpu_manager.get_available_gpus()
        self.selected_gpu: Optional[GPUInfo] = None
        self.benchmark_workers = {}
        
        self.setup_ui()
        self.setup_connections()
        self.refresh_gpu_list()
        
        # Auto-select recommended GPU
        self.auto_select_recommended()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Main group box
        self.gpu_group = QGroupBox("GPU Selection & Configuration")
        gpu_layout = QVBoxLayout(self.gpu_group)
        
        # GPU Selection Section
        selection_frame = QFrame()
        selection_layout = QHBoxLayout(selection_frame)
        
        selection_layout.addWidget(QLabel("Select GPU:"))
        
        self.gpu_combo = QComboBox()
        self.gpu_combo.setMinimumWidth(300)
        selection_layout.addWidget(self.gpu_combo)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setMaximumWidth(80)
        selection_layout.addWidget(self.refresh_btn)
        
        self.benchmark_btn = QPushButton("⚡ Benchmark")
        self.benchmark_btn.setMaximumWidth(100)
        selection_layout.addWidget(self.benchmark_btn)
        
        selection_layout.addStretch()
        gpu_layout.addWidget(selection_frame)
        
        # GPU Information Section
        self.setup_gpu_info_section(gpu_layout)
        
        # Configuration Section
        self.setup_config_section(gpu_layout)
        
        # Performance Section
        self.setup_performance_section(gpu_layout)
        
        layout.addWidget(self.gpu_group)
        layout.addStretch()
    
    def setup_gpu_info_section(self, parent_layout):
        """Setup GPU information display"""
        info_group = QGroupBox("GPU Information")
        info_layout = QGridLayout(info_group)
        
        # GPU details
        self.gpu_name_label = QLabel("No GPU selected")
        self.gpu_memory_label = QLabel("-")
        self.gpu_compute_label = QLabel("-")
        self.gpu_type_label = QLabel("-")
        
        info_layout.addWidget(QLabel("Name:"), 0, 0)
        info_layout.addWidget(self.gpu_name_label, 0, 1)
        info_layout.addWidget(QLabel("Memory:"), 1, 0)
        info_layout.addWidget(self.gpu_memory_label, 1, 1)
        info_layout.addWidget(QLabel("Compute:"), 2, 0)
        info_layout.addWidget(self.gpu_compute_label, 2, 1)
        info_layout.addWidget(QLabel("Type:"), 3, 0)
        info_layout.addWidget(self.gpu_type_label, 3, 1)
        
        # Memory usage bars
        memory_frame = QFrame()
        memory_layout = QVBoxLayout(memory_frame)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setTextVisible(True)
        self.memory_label = QLabel("Memory Usage: 0.0 / 0.0 GB")
        
        memory_layout.addWidget(self.memory_label)
        memory_layout.addWidget(self.memory_progress)
        
        info_layout.addWidget(memory_frame, 0, 2, 4, 1)
        
        parent_layout.addWidget(info_group)
        
        # Setup memory update timer
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(2000)  # Update every 2 seconds
    
    def setup_config_section(self, parent_layout):
        """Setup configuration controls"""
        config_group = QGroupBox("Generation Configuration")
        config_layout = QGridLayout(config_group)
        
        # Resolution
        config_layout.addWidget(QLabel("Resolution:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(256, 2048)
        self.width_spin.setSingleStep(64)
        config_layout.addWidget(self.width_spin, 0, 1)
        
        config_layout.addWidget(QLabel("×"), 0, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(256, 2048)
        self.height_spin.setSingleStep(64)
        config_layout.addWidget(self.height_spin, 0, 3)
        
        # Steps and guidance
        config_layout.addWidget(QLabel("Steps:"), 1, 0)
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 50)
        config_layout.addWidget(self.steps_spin, 1, 1)
        
        config_layout.addWidget(QLabel("Guidance:"), 1, 2)
        self.guidance_spin = QDoubleSpinBox()
        self.guidance_spin.setRange(0.0, 10.0)
        self.guidance_spin.setSingleStep(0.1)
        self.guidance_spin.setDecimals(1)
        config_layout.addWidget(self.guidance_spin, 1, 3)
        
        # Model variant
        config_layout.addWidget(QLabel("Model:"), 2, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["FLUX.1-schnell (Fast)", "FLUX.1-dev (Quality)"])
        config_layout.addWidget(self.model_combo, 2, 1, 1, 3)
        
        # Optimization checkboxes
        self.cpu_offload_check = QCheckBox("CPU Offloading")
        self.attention_slice_check = QCheckBox("Attention Slicing")
        self.vae_slice_check = QCheckBox("VAE Slicing")
        self.fp8_check = QCheckBox("FP8 Precision")
        
        config_layout.addWidget(self.cpu_offload_check, 3, 0, 1, 2)
        config_layout.addWidget(self.attention_slice_check, 3, 2, 1, 2)
        config_layout.addWidget(self.vae_slice_check, 4, 0, 1, 2)
        config_layout.addWidget(self.fp8_check, 4, 2, 1, 2)
        
        # Apply recommended button
        self.apply_recommended_btn = QPushButton("🎯 Apply Recommended Settings")
        config_layout.addWidget(self.apply_recommended_btn, 5, 0, 1, 4)
        
        parent_layout.addWidget(config_group)
    
    def setup_performance_section(self, parent_layout):
        """Setup performance information section"""
        perf_group = QGroupBox("Performance Information")
        perf_layout = QVBoxLayout(perf_group)
        
        # Expected performance
        self.perf_text = QTextEdit()
        self.perf_text.setMaximumHeight(100)
        self.perf_text.setReadOnly(True)
        self.perf_text.setText("Select a GPU to see performance estimates...")
        
        perf_layout.addWidget(self.perf_text)
        
        # Benchmark results
        benchmark_frame = QFrame()
        benchmark_layout = QHBoxLayout(benchmark_frame)
        
        self.benchmark_progress = QProgressBar()
        self.benchmark_progress.setVisible(False)
        benchmark_layout.addWidget(self.benchmark_progress)
        
        self.benchmark_results_label = QLabel("No benchmark data")
        benchmark_layout.addWidget(self.benchmark_results_label)
        
        perf_layout.addWidget(benchmark_frame)
        parent_layout.addWidget(perf_group)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.gpu_combo.currentIndexChanged.connect(self.on_gpu_selected)
        self.refresh_btn.clicked.connect(self.refresh_gpu_list)
        self.benchmark_btn.clicked.connect(self.run_benchmark)
        self.apply_recommended_btn.clicked.connect(self.apply_recommended_settings)
        
        # Config change connections
        self.width_spin.valueChanged.connect(self.on_config_changed)
        self.height_spin.valueChanged.connect(self.on_config_changed)
        self.steps_spin.valueChanged.connect(self.on_config_changed)
        self.guidance_spin.valueChanged.connect(self.on_config_changed)
        self.model_combo.currentTextChanged.connect(self.on_config_changed)
        
        # Checkbox connections
        self.cpu_offload_check.toggled.connect(self.on_config_changed)
        self.attention_slice_check.toggled.connect(self.on_config_changed)
        self.vae_slice_check.toggled.connect(self.on_config_changed)
        self.fp8_check.toggled.connect(self.on_config_changed)
    
    def refresh_gpu_list(self):
        """Refresh the list of available GPUs"""
        self.gpu_combo.clear()
        
        # Re-detect GPUs
        self.gpu_manager = GPUManager()
        self.available_gpus = self.gpu_manager.get_available_gpus()
        
        if not self.available_gpus:
            self.gpu_combo.addItem("No CUDA GPUs detected")
            self.gpu_combo.setEnabled(False)
            return
        
        self.gpu_combo.setEnabled(True)
        
        for gpu in self.available_gpus:
            # Format: "GPU 0: RTX 3070 (8.0 GB)"
            text = f"GPU {gpu.device_id}: {gpu.name} ({gpu.memory_gb:.1f} GB)"
            self.gpu_combo.addItem(text)
            self.gpu_combo.setItemData(self.gpu_combo.count() - 1, gpu.device_id)
        
        self.logger.info(f"Refreshed GPU list: {len(self.available_gpus)} GPUs found")
    
    def auto_select_recommended(self):
        """Auto-select the recommended GPU"""
        recommended = self.gpu_manager.get_recommended_gpu()
        if recommended:
            # Find the combo box index for this GPU
            for i in range(self.gpu_combo.count()):
                if self.gpu_combo.itemData(i) == recommended.device_id:
                    self.gpu_combo.setCurrentIndex(i)
                    break
    
    def on_gpu_selected(self, index: int):
        """Handle GPU selection change"""
        if index < 0 or index >= len(self.available_gpus):
            return
        
        device_id = self.gpu_combo.itemData(index)
        self.selected_gpu = self.gpu_manager.get_gpu_by_id(device_id)
        
        if self.selected_gpu:
            self.update_gpu_info()
            self.apply_recommended_settings()
            self.update_performance_info()
            
            # Enable benchmark button
            self.benchmark_btn.setEnabled(True)
            
            self.logger.info(f"Selected GPU {device_id}: {self.selected_gpu.name}")
    
    def update_gpu_info(self):
        """Update GPU information display"""
        if not self.selected_gpu:
            return
        
        self.gpu_name_label.setText(self.selected_gpu.name)
        self.gpu_memory_label.setText(f"{self.selected_gpu.memory_gb:.1f} GB")
        self.gpu_compute_label.setText(f"{self.selected_gpu.compute_capability[0]}.{self.selected_gpu.compute_capability[1]}")
        
        # Format GPU type nicely
        type_names = {
            GPUType.RTX_3070: "RTX 3070 (8GB VRAM)",
            GPUType.RTX_3080: "RTX 3080 (10GB VRAM)",
            GPUType.RTX_3090: "RTX 3090 (24GB VRAM)",
            GPUType.RTX_4070: "RTX 4070 (12GB VRAM)",
            GPUType.RTX_4080: "RTX 4080 (16GB VRAM)",
            GPUType.RTX_4090: "RTX 4090 (24GB VRAM)",
            GPUType.RTX_5090: "RTX 5090 (32GB VRAM)",
        }
        
        type_display = type_names.get(self.selected_gpu.gpu_type, self.selected_gpu.gpu_type.value.replace('_', ' ').title())
        self.gpu_type_label.setText(type_display)
    
    def update_memory_usage(self):
        """Update memory usage display"""
        if not self.selected_gpu:
            return
        
        memory_stats = self.gpu_manager.get_memory_usage(self.selected_gpu.device_id)
        
        if "error" not in memory_stats:
            allocated = memory_stats["allocated_gb"]
            total = memory_stats["total_gb"]
            
            percentage = int((allocated / total) * 100) if total > 0 else 0
            
            self.memory_progress.setValue(percentage)
            self.memory_label.setText(f"Memory Usage: {allocated:.1f} / {total:.1f} GB ({percentage}%)")
    
    def apply_recommended_settings(self):
        """Apply recommended settings for selected GPU"""
        if not self.selected_gpu:
            return
        
        config = self.selected_gpu.recommended_config
        
        # Set resolution
        self.width_spin.setValue(config["width"])
        self.height_spin.setValue(config["height"])
        
        # Set steps and guidance
        self.steps_spin.setValue(config["num_inference_steps"])
        self.guidance_spin.setValue(config["guidance_scale"])
        
        # Set model variant
        if config.get("model_variant") == "schnell":
            self.model_combo.setCurrentIndex(0)
        else:
            self.model_combo.setCurrentIndex(1)
        
        # Set optimization flags
        self.cpu_offload_check.setChecked(config["enable_cpu_offload"])
        self.attention_slice_check.setChecked(config["enable_attention_slicing"])
        self.vae_slice_check.setChecked(config["enable_vae_slicing"])
        self.fp8_check.setChecked(config["use_fp8"])
        
        self.logger.info(f"Applied recommended settings for {self.selected_gpu.name}")
    
    def update_performance_info(self):
        """Update performance information"""
        if not self.selected_gpu:
            return
        
        profile = self.gpu_manager.get_optimization_profile(self.selected_gpu.gpu_type)
        
        # Estimate performance based on GPU type
        performance_estimates = {
            GPUType.RTX_3070: {"single_image": "8-15 sec", "batch_time": "2-4 min", "quality": "High"},
            GPUType.RTX_3080: {"single_image": "6-10 sec", "batch_time": "1.5-3 min", "quality": "High"},
            GPUType.RTX_3090: {"single_image": "4-8 sec", "batch_time": "1-2 min", "quality": "Ultra"},
            GPUType.RTX_4070: {"single_image": "5-10 sec", "batch_time": "1.5-2.5 min", "quality": "High"},
            GPUType.RTX_4080: {"single_image": "3-6 sec", "batch_time": "45-90 sec", "quality": "Ultra"},
            GPUType.RTX_4090: {"single_image": "2-4 sec", "batch_time": "30-60 sec", "quality": "Ultra"},
            GPUType.RTX_5090: {"single_image": "1-3 sec", "batch_time": "20-45 sec", "quality": "Ultra"},
        }
        
        estimates = performance_estimates.get(self.selected_gpu.gpu_type, 
            {"single_image": "Variable", "batch_time": "Variable", "quality": "Good"})
        
        perf_text = f"""Expected Performance ({profile.name}):
• Single Image: {estimates['single_image']} ({profile.width}×{profile.height})
• Complete Book: {estimates['batch_time']} (8-12 pages)
• Quality Level: {estimates['quality']}
• Model: FLUX.1-{profile.model_variant} ({profile.steps} steps)
• Optimizations: {'CPU Offload, ' if profile.enable_cpu_offload else ''}{'Attention Slicing, ' if profile.enable_attention_slicing else ''}{'VAE Slicing' if profile.enable_vae_slicing else ''}"""
        
        self.perf_text.setText(perf_text)
    
    def run_benchmark(self):
        """Run benchmark on selected GPU"""
        if not self.selected_gpu:
            return
        
        device_id = self.selected_gpu.device_id
        
        if device_id in self.benchmark_workers:
            self.logger.info(f"Benchmark already running for GPU {device_id}")
            return
        
        # Show progress
        self.benchmark_progress.setVisible(True)
        self.benchmark_progress.setRange(0, 0)  # Indeterminate
        self.benchmark_btn.setEnabled(False)
        self.benchmark_results_label.setText("Running benchmark...")
        
        # Start benchmark worker
        worker = GPUBenchmarkWorker(self.gpu_manager, device_id)
        worker.benchmark_completed.connect(self.on_benchmark_completed)
        worker.benchmark_failed.connect(self.on_benchmark_failed)
        worker.finished.connect(lambda: self.cleanup_benchmark_worker(device_id))
        
        self.benchmark_workers[device_id] = worker
        worker.start()
        
        self.logger.info(f"Started benchmark for GPU {device_id}")
    
    def on_benchmark_completed(self, device_id: int, results: Dict):
        """Handle benchmark completion"""
        self.benchmark_progress.setVisible(False)
        self.benchmark_btn.setEnabled(True)
        
        if "error" in results:
            self.benchmark_results_label.setText(f"Benchmark failed: {results['error']}")
        else:
            compute_time = results.get("compute_time_ms", 0)
            score = results.get("utilization_score", 0)
            
            self.benchmark_results_label.setText(
                f"Benchmark: {compute_time:.1f}ms compute, Score: {score:.0f}/100"
            )
        
        self.logger.info(f"Benchmark completed for GPU {device_id}: {results}")
    
    def on_benchmark_failed(self, device_id: int, error: str):
        """Handle benchmark failure"""
        self.benchmark_progress.setVisible(False)
        self.benchmark_btn.setEnabled(True)
        self.benchmark_results_label.setText(f"Benchmark failed: {error}")
        
        self.logger.error(f"Benchmark failed for GPU {device_id}: {error}")
    
    def cleanup_benchmark_worker(self, device_id: int):
        """Clean up benchmark worker"""
        if device_id in self.benchmark_workers:
            del self.benchmark_workers[device_id]
    
    def on_config_changed(self):
        """Handle configuration changes"""
        if self.selected_gpu:
            config = self.get_current_config()
            self.gpu_selected.emit(self.selected_gpu.device_id, config)
    
    def get_current_config(self) -> Dict:
        """Get current configuration from UI"""
        if not self.selected_gpu:
            return {}
        
        model_variant = "schnell" if self.model_combo.currentIndex() == 0 else "dev"
        
        return {
            "device_id": self.selected_gpu.device_id,
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "num_inference_steps": self.steps_spin.value(),
            "guidance_scale": self.guidance_spin.value(),
            "model_variant": model_variant,
            "model_path": f"black-forest-labs/FLUX.1-{model_variant}",
            "enable_cpu_offload": self.cpu_offload_check.isChecked(),
            "enable_sequential_cpu_offload": self.cpu_offload_check.isChecked(),
            "enable_attention_slicing": self.attention_slice_check.isChecked(),
            "enable_vae_slicing": self.vae_slice_check.isChecked(),
            "use_fp8": self.fp8_check.isChecked(),
            "device": f"cuda:{self.selected_gpu.device_id}",
            "dtype": "float16"
        }
    
    def get_selected_gpu_info(self) -> Optional[GPUInfo]:
        """Get currently selected GPU info"""
        return self.selected_gpu
    
    def clear_gpu_cache(self):
        """Clear GPU cache for selected GPU"""
        if self.selected_gpu:
            self.gpu_manager.clear_gpu_cache(self.selected_gpu.device_id)
            self.logger.info(f"Cleared cache for GPU {self.selected_gpu.device_id}")
    
    def closeEvent(self, event):
        """Handle widget close"""
        # Stop memory timer
        if hasattr(self, 'memory_timer'):
            self.memory_timer.stop()
        
        # Stop any running benchmarks
        for worker in self.benchmark_workers.values():
            if worker.isRunning():
                worker.terminate()
                worker.wait(1000)
        
        super().closeEvent(event)