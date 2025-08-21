"""
GPU Detection and Management System
Handles multi-GPU environments and optimal configuration selection
"""

import torch
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class GPUType(Enum):
    """GPU type classifications for optimization"""
    RTX_3070 = "rtx_3070"
    RTX_3080 = "rtx_3080" 
    RTX_3090 = "rtx_3090"
    RTX_4070 = "rtx_4070"
    RTX_4080 = "rtx_4080"
    RTX_4090 = "rtx_4090"
    RTX_5090 = "rtx_5090"
    OTHER_8GB = "other_8gb"
    OTHER_12GB = "other_12gb"
    OTHER_16GB = "other_16gb"
    OTHER_24GB = "other_24gb"
    UNKNOWN = "unknown"

@dataclass
class GPUInfo:
    """Information about a detected GPU"""
    device_id: int
    name: str
    memory_gb: float
    compute_capability: Tuple[int, int]
    gpu_type: GPUType
    recommended_config: Dict
    is_available: bool = True

@dataclass 
class OptimizationProfile:
    """Optimization profile for specific GPU types"""
    name: str
    width: int
    height: int
    steps: int
    guidance_scale: float
    enable_cpu_offload: bool
    enable_sequential_offload: bool
    enable_attention_slicing: bool
    enable_vae_slicing: bool
    use_fp8: bool
    memory_fraction: float
    batch_size: int
    model_variant: str  # schnell or dev

class GPUManager:
    """Manages GPU detection, selection, and optimization profiles"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_gpus: List[GPUInfo] = []
        self.optimization_profiles: Dict[GPUType, OptimizationProfile] = {}
        self._setup_optimization_profiles()
        self._detect_gpus()
    
    def _setup_optimization_profiles(self):
        """Setup optimization profiles for different GPU types"""
        
        # RTX 3070 (8GB) - Memory constrained
        self.optimization_profiles[GPUType.RTX_3070] = OptimizationProfile(
            name="RTX 3070 (8GB)",
            width=512,
            height=768,
            steps=4,
            guidance_scale=0.0,
            enable_cpu_offload=True,
            enable_sequential_offload=True,
            enable_attention_slicing=True,
            enable_vae_slicing=True,
            use_fp8=False,
            memory_fraction=0.85,
            batch_size=1,
            model_variant="schnell"
        )
        
        # RTX 3080 (10GB) - Balanced
        self.optimization_profiles[GPUType.RTX_3080] = OptimizationProfile(
            name="RTX 3080 (10GB)",
            width=768,
            height=768,
            steps=4,
            guidance_scale=0.0,
            enable_cpu_offload=False,
            enable_sequential_offload=False,
            enable_attention_slicing=True,
            enable_vae_slicing=True,
            use_fp8=False,
            memory_fraction=0.9,
            batch_size=1,
            model_variant="schnell"
        )
        
        # RTX 3090 (24GB) - High memory
        self.optimization_profiles[GPUType.RTX_3090] = OptimizationProfile(
            name="RTX 3090 (24GB)",
            width=1024,
            height=1024,
            steps=28,
            guidance_scale=1.0,
            enable_cpu_offload=False,
            enable_sequential_offload=False,
            enable_attention_slicing=False,
            enable_vae_slicing=False,
            use_fp8=False,
            memory_fraction=0.9,
            batch_size=2,
            model_variant="dev"
        )
        
        # RTX 4070 (12GB) - Modern efficiency
        self.optimization_profiles[GPUType.RTX_4070] = OptimizationProfile(
            name="RTX 4070 (12GB)",
            width=768,
            height=1024,
            steps=4,
            guidance_scale=0.0,
            enable_cpu_offload=False,
            enable_sequential_offload=False,
            enable_attention_slicing=True,
            enable_vae_slicing=False,
            use_fp8=False,
            memory_fraction=0.9,
            batch_size=1,
            model_variant="schnell"
        )
        
        # RTX 4080 (16GB) - High performance
        self.optimization_profiles[GPUType.RTX_4080] = OptimizationProfile(
            name="RTX 4080 (16GB)",
            width=1024,
            height=1024,
            steps=28,
            guidance_scale=1.0,
            enable_cpu_offload=False,
            enable_sequential_offload=False,
            enable_attention_slicing=False,
            enable_vae_slicing=False,
            use_fp8=False,
            memory_fraction=0.9,
            batch_size=2,
            model_variant="dev"
        )
        
        # RTX 4090 (24GB) - Flagship
        self.optimization_profiles[GPUType.RTX_4090] = OptimizationProfile(
            name="RTX 4090 (24GB)",
            width=1024,
            height=1024,
            steps=28,
            guidance_scale=1.0,
            enable_cpu_offload=False,
            enable_sequential_offload=False,
            enable_attention_slicing=False,
            enable_vae_slicing=False,
            use_fp8=False,
            memory_fraction=0.95,
            batch_size=4,
            model_variant="dev"
        )
        
        # RTX 5090 (32GB) - Ultimate
        self.optimization_profiles[GPUType.RTX_5090] = OptimizationProfile(
            name="RTX 5090 (32GB)",
            width=1024,
            height=1024,
            steps=28,
            guidance_scale=1.0,
            enable_cpu_offload=False,
            enable_sequential_offload=False,
            enable_attention_slicing=False,
            enable_vae_slicing=False,
            use_fp8=True,
            memory_fraction=0.95,
            batch_size=8,
            model_variant="dev"
        )
        
        # Generic profiles based on memory
        self.optimization_profiles[GPUType.OTHER_8GB] = self.optimization_profiles[GPUType.RTX_3070]
        self.optimization_profiles[GPUType.OTHER_12GB] = self.optimization_profiles[GPUType.RTX_4070]
        self.optimization_profiles[GPUType.OTHER_16GB] = self.optimization_profiles[GPUType.RTX_4080]
        self.optimization_profiles[GPUType.OTHER_24GB] = self.optimization_profiles[GPUType.RTX_4090]
    
    def _detect_gpus(self):
        """Detect all available GPUs and their capabilities"""
        
        if not torch.cuda.is_available():
            self.logger.warning("CUDA not available - no GPUs detected")
            return
        
        gpu_count = torch.cuda.device_count()
        self.logger.info(f"Detected {gpu_count} GPU(s)")
        
        for i in range(gpu_count):
            try:
                # Get GPU properties
                props = torch.cuda.get_device_properties(i)
                memory_gb = props.total_memory / (1024**3)
                compute_cap = (props.major, props.minor)
                
                # Classify GPU type
                gpu_type = self._classify_gpu(props.name, memory_gb, compute_cap)
                
                # Get optimization profile
                profile = self.optimization_profiles.get(gpu_type, 
                    self.optimization_profiles[GPUType.OTHER_8GB])
                
                # Create GPU info
                gpu_info = GPUInfo(
                    device_id=i,
                    name=props.name,
                    memory_gb=memory_gb,
                    compute_capability=compute_cap,
                    gpu_type=gpu_type,
                    recommended_config=self._profile_to_config(profile),
                    is_available=True
                )
                
                self.available_gpus.append(gpu_info)
                
                self.logger.info(f"GPU {i}: {props.name} ({memory_gb:.1f}GB) - {gpu_type.value}")
                
            except Exception as e:
                self.logger.error(f"Failed to detect GPU {i}: {e}")
    
    def _classify_gpu(self, name: str, memory_gb: float, compute_cap: Tuple[int, int]) -> GPUType:
        """Classify GPU type based on name and specifications"""
        
        name_lower = name.lower()
        
        # RTX 30 series
        if "3070" in name_lower:
            return GPUType.RTX_3070
        elif "3080" in name_lower:
            return GPUType.RTX_3080  
        elif "3090" in name_lower:
            return GPUType.RTX_3090
        
        # RTX 40 series
        elif "4070" in name_lower:
            return GPUType.RTX_4070
        elif "4080" in name_lower:
            return GPUType.RTX_4080
        elif "4090" in name_lower:
            return GPUType.RTX_4090
        
        # RTX 50 series
        elif "5090" in name_lower:
            return GPUType.RTX_5090
        
        # Generic classification by memory
        elif memory_gb >= 30:
            return GPUType.OTHER_24GB
        elif memory_gb >= 20:
            return GPUType.OTHER_24GB
        elif memory_gb >= 14:
            return GPUType.OTHER_16GB
        elif memory_gb >= 10:
            return GPUType.OTHER_12GB
        elif memory_gb >= 6:
            return GPUType.OTHER_8GB
        else:
            return GPUType.UNKNOWN
    
    def _profile_to_config(self, profile: OptimizationProfile) -> Dict:
        """Convert optimization profile to configuration dictionary"""
        return {
            "width": profile.width,
            "height": profile.height,
            "num_inference_steps": profile.steps,
            "guidance_scale": profile.guidance_scale,
            "enable_cpu_offload": profile.enable_cpu_offload,
            "enable_sequential_cpu_offload": profile.enable_sequential_offload,
            "enable_attention_slicing": profile.enable_attention_slicing,
            "enable_vae_slicing": profile.enable_vae_slicing,
            "use_fp8": profile.use_fp8,
            "memory_fraction": profile.memory_fraction,
            "batch_size": profile.batch_size,
            "model_variant": profile.model_variant,
            "model_path": f"black-forest-labs/FLUX.1-{profile.model_variant}"
        }
    
    def get_available_gpus(self) -> List[GPUInfo]:
        """Get list of all available GPUs"""
        return self.available_gpus
    
    def get_gpu_by_id(self, device_id: int) -> Optional[GPUInfo]:
        """Get GPU info by device ID"""
        for gpu in self.available_gpus:
            if gpu.device_id == device_id:
                return gpu
        return None
    
    def get_recommended_gpu(self) -> Optional[GPUInfo]:
        """Get the recommended GPU (highest memory, best performance)"""
        if not self.available_gpus:
            return None
        
        # Sort by memory (descending) and prefer newer architectures
        def gpu_score(gpu: GPUInfo) -> float:
            base_score = gpu.memory_gb
            # Bonus for newer compute capabilities
            if gpu.compute_capability[0] >= 9:  # RTX 50 series
                base_score += 10
            elif gpu.compute_capability[0] >= 8 and gpu.compute_capability[1] >= 9:  # RTX 40 series
                base_score += 5
            elif gpu.compute_capability[0] >= 8 and gpu.compute_capability[1] >= 6:  # RTX 30 series
                base_score += 2
            return base_score
        
        return max(self.available_gpus, key=gpu_score)
    
    def get_optimization_profile(self, gpu_type: GPUType) -> OptimizationProfile:
        """Get optimization profile for GPU type"""
        return self.optimization_profiles.get(gpu_type, 
            self.optimization_profiles[GPUType.OTHER_8GB])
    
    def create_flux_config(self, gpu_info: GPUInfo):
        """Create FLUX configuration for specific GPU"""
        from generators.flux_comfyui_generator import FluxConfig
        
        config_dict = gpu_info.recommended_config
        
        return FluxConfig(
            model_path=config_dict["model_path"],
            width=config_dict["width"],
            height=config_dict["height"],
            num_inference_steps=config_dict["num_inference_steps"],
            guidance_scale=config_dict["guidance_scale"],
            device=f"cuda:{gpu_info.device_id}",
            dtype=torch.float16,
            use_fp8=config_dict["use_fp8"],
            enable_cpu_offload=config_dict["enable_cpu_offload"],
            enable_sequential_cpu_offload=config_dict["enable_sequential_cpu_offload"]
        )
    
    def benchmark_gpu(self, gpu_info: GPUInfo) -> Dict[str, float]:
        """Run a quick benchmark on specific GPU"""
        try:
            device = f"cuda:{gpu_info.device_id}"
            
            # Simple memory and compute benchmark
            start_time = torch.cuda.Event(enable_timing=True)
            end_time = torch.cuda.Event(enable_timing=True)
            
            # Memory test
            with torch.cuda.device(device):
                torch.cuda.empty_cache()
                
                start_time.record()
                # Allocate and compute
                x = torch.randn(1024, 1024, device=device, dtype=torch.float16)
                y = torch.mm(x, x.T)
                result = torch.sum(y)
                end_time.record()
                
                torch.cuda.synchronize()
                compute_time = start_time.elapsed_time(end_time)
                
                # Memory stats
                allocated = torch.cuda.memory_allocated(device) / (1024**3)
                cached = torch.cuda.memory_reserved(device) / (1024**3)
                
                del x, y, result
                torch.cuda.empty_cache()
            
            return {
                "compute_time_ms": compute_time,
                "memory_allocated_gb": allocated,
                "memory_cached_gb": cached,
                "memory_total_gb": gpu_info.memory_gb,
                "utilization_score": min(100, (1000 / compute_time) * 10)  # Arbitrary score
            }
            
        except Exception as e:
            self.logger.error(f"Benchmark failed for GPU {gpu_info.device_id}: {e}")
            return {"error": str(e)}
    
    def get_memory_usage(self, device_id: int) -> Dict[str, float]:
        """Get current memory usage for specific GPU"""
        try:
            device = f"cuda:{device_id}"
            return {
                "allocated_gb": torch.cuda.memory_allocated(device) / (1024**3),
                "reserved_gb": torch.cuda.memory_reserved(device) / (1024**3),
                "max_allocated_gb": torch.cuda.max_memory_allocated(device) / (1024**3),
                "total_gb": torch.cuda.get_device_properties(device).total_memory / (1024**3)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def clear_gpu_cache(self, device_id: Optional[int] = None):
        """Clear GPU cache for specific device or all devices"""
        try:
            if device_id is not None:
                with torch.cuda.device(device_id):
                    torch.cuda.empty_cache()
                    torch.cuda.reset_peak_memory_stats()
            else:
                torch.cuda.empty_cache()
                for i in range(torch.cuda.device_count()):
                    torch.cuda.reset_peak_memory_stats(i)
            
            self.logger.info(f"Cleared GPU cache for device {device_id if device_id else 'all'}")
            
        except Exception as e:
            self.logger.error(f"Failed to clear GPU cache: {e}")
    
    def set_gpu_power_state(self, device_id: int, high_performance: bool = True):
        """Set GPU to high performance mode (if supported)"""
        # This would interface with nvidia-ml-py or nvidia-smi
        # For now, just log the request
        mode = "high performance" if high_performance else "power saving"
        self.logger.info(f"Setting GPU {device_id} to {mode} mode")
    
    def get_gpu_stats_summary(self) -> Dict:
        """Get summary of all GPU statistics"""
        summary = {
            "total_gpus": len(self.available_gpus),
            "total_memory_gb": sum(gpu.memory_gb for gpu in self.available_gpus),
            "gpu_types": {},
            "recommended_gpu": None
        }
        
        # Count GPU types
        for gpu in self.available_gpus:
            gpu_type_name = gpu.gpu_type.value
            if gpu_type_name not in summary["gpu_types"]:
                summary["gpu_types"][gpu_type_name] = 0
            summary["gpu_types"][gpu_type_name] += 1
        
        # Get recommended GPU
        recommended = self.get_recommended_gpu()
        if recommended:
            summary["recommended_gpu"] = {
                "device_id": recommended.device_id,
                "name": recommended.name,
                "memory_gb": recommended.memory_gb,
                "type": recommended.gpu_type.value
            }
        
        return summary