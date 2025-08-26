"""
Story to Prompt Generator (Local LLM) - ComfyUI Custom Node
A simplified node that converts narrative text into multiple AI-ready prompts using locally loaded LLM models.
"""

import os
import re
import torch
from typing import List, Tuple, Any, Optional
import folder_paths

# Try to import transformers, with fallback handling
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers not installed. Please install with: pip install transformers")

class StoryToPromptGeneratorLocal:
    """
    A ComfyUI custom node that converts narrative text into multiple AI-ready prompts
    using locally loaded LLM models via transformers.
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.current_model_name = None
    
    @classmethod
    def INPUT_TYPES(cls):
        # Get available models from the LLMs folder
        llm_models = cls._get_available_models()
        
        return {
            "required": {
                "story": ("STRING", {
                    "multiline": True,
                    "default": "Enter your story here...",
                    "placeholder": "Narrative text to convert into prompts"
                }),
                "model": (llm_models, {
                    "default": llm_models[0] if llm_models else "No models found"
                }),
                "prompt_count": ("INT", {
                    "default": 6,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "display": "number"
                }),
                "generation_mode": (["balanced", "detailed", "cinematic"], {
                    "default": "balanced"
                })
            }
        }
    
    @classmethod
    def _get_available_models(cls) -> List[str]:
        """
        Get list of available LLM models from the models/LLMs folder.
        """
        try:
            models_dir = folder_paths.models_dir
            llm_dir = os.path.join(models_dir, "LLMs")
            
            if not os.path.exists(llm_dir):
                os.makedirs(llm_dir, exist_ok=True)
                return ["Download models to models/LLMs folder - See instructions"]
            
            model_folders = []
            for item in os.listdir(llm_dir):
                item_path = os.path.join(llm_dir, item)
                if os.path.isdir(item_path):
                    # Check if it contains model files
                    has_model_files = any(f.endswith(('.bin', '.safetensors', '.pt')) for f in os.listdir(item_path))
                    has_config = os.path.exists(os.path.join(item_path, 'config.json'))
                    
                    if has_model_files and has_config:
                        model_folders.append(item)
                    else:
                        print(f"Incomplete model in {item}: missing model files or config")
            
            if not model_folders:
                return ["Download complete models to models/LLMs folder - See instructions"]
            
            # Add download instructions as first option
            result = ["📖 Download Instructions"] + sorted(model_folders)
            return result
            
        except Exception as e:
            print(f"Error getting models: {e}")
            return ["Error accessing models folder"]
    
    RETURN_TYPES = tuple(["STRING"] * 10)
    RETURN_NAMES = tuple([f"prompt_{i+1}" for i in range(10)])
    FUNCTION = "generate_prompts"
    CATEGORY = "conditioning"
    
    OUTPUT_NODE = False
    
    def generate_prompts(self, story: str, model: str, prompt_count: int, 
                        generation_mode: str) -> Tuple[str, ...]:
        """
        Main function to convert story into multiple prompts using local LLM.
        """
        
        if not TRANSFORMERS_AVAILABLE:
            error_msg = "Transformers library not installed. Please install with: pip install transformers"
            return tuple([error_msg] + [""] * 9)
        
        if not story.strip():
            return tuple([""] * 10)
        
        if model.startswith("Download") or model.startswith("Error") or model.startswith("📖"):
            instructions = """
DOWNLOAD INSTRUCTIONS FOR LLM MODELS:

Best Free Models (choose one):

1. Mistral-7B-Instruct-v0.3 (RECOMMENDED):
   pip install huggingface_hub
   python -c "from huggingface_hub import snapshot_download; snapshot_download('mistralai/Mistral-7B-Instruct-v0.3', local_dir='./ComfyUI/models/LLMs/Mistral-7B-Instruct-v0.3')"

2. Zephyr-7B-Beta (GOOD ALTERNATIVE):
   python -c "from huggingface_hub import snapshot_download; snapshot_download('HuggingFaceH4/zephyr-7b-beta', local_dir='./ComfyUI/models/LLMs/zephyr-7b-beta')"

3. DialoGPT-Large (SMALLER, FASTER):
   python -c "from huggingface_hub import snapshot_download; snapshot_download('microsoft/DialoGPT-large', local_dir='./ComfyUI/models/LLMs/DialoGPT-large')"

Or manually download from:
- https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3
- https://huggingface.co/HuggingFaceH4/zephyr-7b-beta
- https://huggingface.co/microsoft/DialoGPT-large

After download, restart ComfyUI to see the models in the dropdown.
            """
            return tuple([instructions] + [""] * 9)
        
        # Force regeneration with timestamp
        import time
        timestamp = str(int(time.time() * 1000))
        print(f"Generation timestamp: {timestamp}")
        
        try:
            # Load model if needed
            if not self._load_model(model):
                error_msg = f"Failed to load model: {model}"
                return tuple([error_msg] + [""] * 9)
            
            # Generate prompts using LLM
            print(f"Generating {prompt_count} prompts with LLM: {model}")
            prompts = self._generate_with_llm(story, prompt_count, generation_mode)
            
            # Ensure we have exactly prompt_count prompts filled
            print(f"Generated {len(prompts)} prompts, need {prompt_count}")
            
            # Fill missing prompts if we don't have enough
            while len(prompts) < prompt_count:
                # Create additional prompts based on the story
                additional_prompt = f"Scene {len(prompts) + 1} from the story: {story[:100]}..., highly detailed, professional quality, beautiful composition"
                prompts.append(additional_prompt)
                print(f"Added fallback prompt {len(prompts)}: {additional_prompt[:50]}...")
            
            # Ensure we have exactly 10 outputs (pad unused pins with empty strings)
            final_outputs = []
            for i in range(10):
                if i < prompt_count and i < len(prompts):
                    final_outputs.append(prompts[i])
                    print(f"Pin {i+1}: {prompts[i][:80]}...")
                else:
                    final_outputs.append("")  # Empty for unused pins
            
            return tuple(final_outputs)
            
        except Exception as e:
            error_msg = f"Generation Error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return tuple([error_msg] + [""] * 9)
    
    def _load_model(self, model_name: str) -> bool:
        """
        Load the specified model if not already loaded.
        """
        if self.current_model_name == model_name and self.pipeline is not None:
            return True
        
        try:
            print(f"Loading model: {model_name}")
            
            # Get model path
            models_dir = folder_paths.models_dir
            model_path = os.path.join(models_dir, "LLMs", model_name)
            
            if not os.path.exists(model_path):
                print(f"Model path not found: {model_path}")
                return False
            
            # Clear previous model from memory
            if self.model is not None:
                del self.model
                del self.tokenizer
                del self.pipeline
                torch.cuda.empty_cache()
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path, 
                local_files_only=True,
                trust_remote_code=True
            )
            
            # Add pad token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            if device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    local_files_only=True,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    low_cpu_mem_usage=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    local_files_only=True,
                    trust_remote_code=True,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                ).to(device)
            
            # Create pipeline (don't specify device when using accelerate/device_map)
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer
            )
            
            self.current_model_name = model_name
            print(f"Successfully loaded model: {model_name}")
            return True
            
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            self.model = None
            self.tokenizer = None
            self.pipeline = None
            self.current_model_name = None
            return False
    
    def _generate_with_llm(self, story: str, prompt_count: int, generation_mode: str) -> List[str]:
        """
        Generate prompts using the loaded local LLM - simplified version.
        """
        
        # Create a clear, simple instruction
        mode_instruction = {
            "detailed": "Create hyperrealistic, highly detailed image prompts with intricate details.",
            "cinematic": "Create cinematic, movie-like image prompts with dramatic lighting.",
            "balanced": "Create professional, high-quality image prompts."
        }
        
        instruction = mode_instruction.get(generation_mode, mode_instruction["balanced"])
        
        prompt = f"""{instruction}

Story: {story}

Create {prompt_count} image generation prompts from this story.
Format as numbered list:

1."""
        
        try:
            print("Generating with LLM...")
            result = self.pipeline(
                prompt,
                max_new_tokens=500,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )
            
            # Extract text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0]['generated_text']
            else:
                generated_text = str(result)
            
            print(f"Generated text (first 200 chars): {generated_text[:200]}...")
            
            # Simple parsing - just look for lines that seem like prompts
            full_text = "1." + generated_text
            lines = full_text.split('\n')
            
            prompts = []
            for line in lines:
                line = line.strip()
                
                # Look for numbered lines or substantial content
                if (len(line) > 20 and 
                    (re.match(r'^\d+\.', line) or 
                     not line.lower().startswith(('create', 'format', 'story', 'prompt')))):
                    
                    # Clean up the line
                    clean_line = re.sub(r'^\d+\.\s*', '', line)  # Remove numbering
                    clean_line = clean_line.strip()
                    
                    if len(clean_line) > 15:  # Only keep substantial prompts
                        prompts.append(clean_line)
                        print(f"Found prompt: {clean_line[:80]}...")
                        
                        if len(prompts) >= prompt_count:
                            break
            
            print(f"Extracted {len(prompts)} prompts")
            return prompts
            
        except Exception as e:
            print(f"LLM generation error: {e}")
            return []


# Node mapping for ComfyUI
NODE_CLASS_MAPPINGS = {
    "StoryToPromptGeneratorLocal": StoryToPromptGeneratorLocal
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StoryToPromptGeneratorLocal": "Story to Prompt Generator (Local LLM)"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']