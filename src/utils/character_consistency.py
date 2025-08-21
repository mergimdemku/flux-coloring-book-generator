"""
Character consistency system for maintaining same character across coloring book pages
"""

import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from PIL import Image
import numpy as np
import logging

class CharacterConsistencyManager:
    """Manages character consistency across coloring book pages"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.character_profiles = {}
        
        # Consistency strategies
        self.strategies = {
            'seed_based': self._apply_seed_consistency,
            'prompt_template': self._apply_prompt_template,
            'reference_guided': self._apply_reference_guidance
        }
    
    def create_character_profile(self, character_name: str, character_description: str, 
                               base_seed: Optional[int] = None) -> Dict[str, Any]:
        """Create a character consistency profile"""
        
        # Generate character ID from description
        char_id = self._generate_character_id(character_name, character_description)
        
        # Create base seed if not provided
        if base_seed is None:
            base_seed = self._generate_seed_from_description(character_description)
        
        profile = {
            'character_id': char_id,
            'name': character_name,
            'description': character_description,
            'base_seed': base_seed,
            'created_at': Path(__file__).stat().st_mtime,  # Current time
            'consistency_keywords': self._extract_consistency_keywords(character_description),
            'prompt_template': self._create_prompt_template(character_name, character_description),
            'seed_variants': self._generate_seed_variants(base_seed),
            'appearance_locks': self._create_appearance_locks(character_description)
        }
        
        self.character_profiles[char_id] = profile
        self.logger.info(f"Created character profile for {character_name} (ID: {char_id})")
        
        return profile
    
    def _generate_character_id(self, name: str, description: str) -> str:
        """Generate unique character ID from name and description"""
        
        combined = f"{name.lower()}:{description.lower()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _generate_seed_from_description(self, description: str) -> int:
        """Generate deterministic seed from character description"""
        
        # Use hash of description to create consistent seed
        hash_obj = hashlib.sha256(description.encode())
        seed = int(hash_obj.hexdigest()[:8], 16) % (2**31 - 1)  # 32-bit positive int
        
        return seed
    
    def _extract_consistency_keywords(self, description: str) -> List[str]:
        """Extract key visual elements that must remain consistent"""
        
        # Important visual keywords that affect character appearance
        visual_keywords = [
            'small', 'large', 'tiny', 'big', 'tall', 'short',
            'brown', 'black', 'white', 'gray', 'golden', 'red', 'blue', 'green',
            'floppy', 'pointed', 'round', 'square', 'long', 'short',
            'striped', 'spotted', 'plain', 'patterned',
            'collar', 'tag', 'bow', 'hat', 'scarf',
            'ears', 'nose', 'tail', 'eyes', 'paws',
            'fluffy', 'smooth', 'curly', 'straight'
        ]
        
        description_lower = description.lower()
        found_keywords = []
        
        for keyword in visual_keywords:
            if keyword in description_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _create_prompt_template(self, name: str, description: str) -> str:
        """Create a standardized prompt template for consistency"""
        
        # Clean and standardize the description
        cleaned_desc = self._clean_description_for_prompt(description)
        
        template = f"{name}: {cleaned_desc}, consistent character design, same appearance throughout, identical features"
        
        return template
    
    def _clean_description_for_prompt(self, description: str) -> str:
        """Clean character description for optimal prompt use"""
        
        # Remove redundant words and phrases
        cleanup_patterns = [
            'the character', 'this character', 'character',
            'should be', 'must be', 'needs to be',
            'always', 'throughout the book'
        ]
        
        cleaned = description.lower()
        for pattern in cleanup_patterns:
            cleaned = cleaned.replace(pattern, '')
        
        # Normalize spacing
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _generate_seed_variants(self, base_seed: int, count: int = 10) -> List[int]:
        """Generate seed variants for different scenes while maintaining consistency"""
        
        variants = []
        
        # Use base seed for main character scenes
        variants.append(base_seed)
        
        # Generate variants by adding small offsets
        for i in range(1, count):
            # Small incremental changes to allow scene variety
            # while keeping character consistent
            variant = base_seed + (i * 7)  # Prime number for good distribution
            variants.append(variant % (2**31 - 1))
        
        return variants
    
    def _create_appearance_locks(self, description: str) -> Dict[str, str]:
        """Create appearance locks for critical character features"""
        
        locks = {}
        description_lower = description.lower()
        
        # Extract specific locked features
        if 'collar' in description_lower:
            collar_desc = self._extract_feature_description(description, 'collar')
            locks['collar'] = collar_desc
        
        if any(ear_type in description_lower for ear_type in ['floppy', 'pointed', 'round']):
            ear_desc = self._extract_feature_description(description, 'ear')
            locks['ears'] = ear_desc
        
        if 'nose' in description_lower:
            nose_desc = self._extract_feature_description(description, 'nose')  
            locks['nose'] = nose_desc
        
        if 'tag' in description_lower:
            tag_desc = self._extract_feature_description(description, 'tag')
            locks['tag'] = tag_desc
        
        return locks
    
    def _extract_feature_description(self, full_description: str, feature: str) -> str:
        """Extract description of specific feature"""
        
        words = full_description.lower().split()
        
        try:
            feature_idx = None
            for i, word in enumerate(words):
                if feature in word:
                    feature_idx = i
                    break
            
            if feature_idx is not None:
                # Get surrounding context (2 words before and after)
                start = max(0, feature_idx - 2)
                end = min(len(words), feature_idx + 3)
                context = ' '.join(words[start:end])
                return context
        except:
            pass
        
        return f"{feature} as described"
    
    def apply_consistency_strategy(self, prompts: List[Dict[str, Any]], 
                                 character_profile: Dict[str, Any],
                                 strategy: str = 'seed_based') -> List[Dict[str, Any]]:
        """Apply consistency strategy to prompts"""
        
        if strategy not in self.strategies:
            self.logger.warning(f"Unknown strategy: {strategy}. Using 'seed_based'")
            strategy = 'seed_based'
        
        return self.strategies[strategy](prompts, character_profile)
    
    def _apply_seed_consistency(self, prompts: List[Dict[str, Any]], 
                               character_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply seed-based consistency strategy"""
        
        base_seed = character_profile['base_seed']
        seed_variants = character_profile['seed_variants']
        
        consistent_prompts = []
        
        for i, prompt_data in enumerate(prompts):
            modified_prompt = prompt_data.copy()
            
            # Assign seed based on page type
            page_type = prompt_data.get('page_type', 'scene')
            
            if page_type == 'scene':
                # Main story scenes use base seed for maximum consistency
                scene_info = prompt_data.get('scene_info', {})
                scene_num = scene_info.get('scene_number', 1)
                
                # Use base seed with small scene-specific variation
                seed_index = min(scene_num - 1, len(seed_variants) - 1)
                assigned_seed = seed_variants[seed_index]
                
            elif page_type == 'cover':
                # Cover uses base seed
                assigned_seed = base_seed
                
            elif page_type == 'back_cover':
                # Back cover uses base seed + offset
                assigned_seed = base_seed + 100
                
            else:  # activity pages
                # Activity pages can have more variation
                assigned_seed = base_seed + 1000 + i
            
            modified_prompt['generation_seed'] = assigned_seed
            modified_prompt['consistency_applied'] = True
            modified_prompt['character_id'] = character_profile['character_id']
            
            consistent_prompts.append(modified_prompt)
        
        self.logger.info(f"Applied seed consistency to {len(prompts)} prompts")
        return consistent_prompts
    
    def _apply_prompt_template(self, prompts: List[Dict[str, Any]], 
                              character_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply prompt template consistency strategy"""
        
        template = character_profile['prompt_template']
        consistency_keywords = character_profile['consistency_keywords']
        
        consistent_prompts = []
        
        for prompt_data in prompts:
            modified_prompt = prompt_data.copy()
            original_prompt = prompt_data['prompt']
            
            # Replace character description with consistent template
            enhanced_prompt = self._merge_prompt_with_template(original_prompt, template, consistency_keywords)
            
            modified_prompt['prompt'] = enhanced_prompt
            modified_prompt['original_prompt'] = original_prompt
            modified_prompt['consistency_applied'] = True
            modified_prompt['character_id'] = character_profile['character_id']
            
            consistent_prompts.append(modified_prompt)
        
        self.logger.info(f"Applied prompt template consistency to {len(prompts)} prompts")
        return consistent_prompts
    
    def _merge_prompt_with_template(self, original_prompt: str, template: str, 
                                   keywords: List[str]) -> str:
        """Merge original prompt with character template"""
        
        # Find character description in original prompt
        # Usually appears after the character name
        prompt_parts = original_prompt.split(',')
        
        # Replace or enhance character description
        enhanced_parts = []
        template_inserted = False
        
        for part in prompt_parts:
            part_stripped = part.strip()
            
            # If this part contains character info, replace with template
            if any(keyword in part_stripped.lower() for keyword in keywords):
                if not template_inserted:
                    enhanced_parts.append(template)
                    template_inserted = True
                # Skip the original character description
            else:
                enhanced_parts.append(part_stripped)
        
        # If template wasn't inserted, add it at the beginning
        if not template_inserted:
            enhanced_parts.insert(1, template)  # After the base style
        
        return ', '.join(enhanced_parts)
    
    def _apply_reference_guidance(self, prompts: List[Dict[str, Any]], 
                                 character_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply reference-guided consistency (for future implementation)"""
        
        # This would use a reference image of the character
        # For now, combine seed and prompt strategies
        
        prompts = self._apply_seed_consistency(prompts, character_profile)
        prompts = self._apply_prompt_template(prompts, character_profile)
        
        for prompt_data in prompts:
            prompt_data['consistency_strategy'] = 'reference_guided'
        
        return prompts
    
    def validate_character_consistency(self, generated_images: List[Image.Image],
                                     character_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate character consistency across generated images"""
        
        results = {
            'character_id': character_profile['character_id'],
            'character_name': character_profile['name'],
            'consistency_score': 0,
            'issues': [],
            'recommendations': []
        }
        
        if len(generated_images) < 2:
            results['consistency_score'] = 100  # Can't evaluate with less than 2 images
            return results
        
        # Basic consistency checks (would need more sophisticated image analysis)
        try:
            # Simple color consistency check
            color_consistency = self._check_color_consistency(generated_images)
            
            # Basic shape consistency (simplified)
            shape_consistency = self._check_shape_consistency(generated_images)
            
            # Calculate overall score
            consistency_score = (color_consistency + shape_consistency) / 2
            results['consistency_score'] = consistency_score
            
            if consistency_score < 70:
                results['issues'].append({
                    'type': 'low_consistency',
                    'message': f"Character consistency is below acceptable threshold ({consistency_score:.1f}%)",
                    'severity': 'major'
                })
                
                results['recommendations'].append(
                    "Consider using seed-based consistency with smaller seed variations"
                )
                results['recommendations'].append(
                    "Ensure character description is detailed and specific"
                )
        
        except Exception as e:
            self.logger.error(f"Consistency validation failed: {e}")
            results['issues'].append({
                'type': 'validation_error',
                'message': f"Could not validate consistency: {str(e)}",
                'severity': 'critical'
            })
        
        return results
    
    def _check_color_consistency(self, images: List[Image.Image]) -> float:
        """Check color consistency across images (simplified)"""
        
        # Convert to grayscale and check histogram similarity
        histograms = []
        
        for image in images:
            gray = image.convert('L')
            # Focus on darker areas (where character would be)
            np_image = np.array(gray)
            dark_pixels = np_image[np_image < 128]
            
            if len(dark_pixels) > 0:
                hist, _ = np.histogram(dark_pixels, bins=32, range=(0, 128))
                histograms.append(hist / np.sum(hist))  # Normalize
        
        if len(histograms) < 2:
            return 100  # No comparison possible
        
        # Compare histograms pairwise
        similarities = []
        
        for i in range(len(histograms)):
            for j in range(i + 1, len(histograms)):
                # Chi-square distance (simplified)
                hist1, hist2 = histograms[i], histograms[j]
                
                # Avoid division by zero
                eps = 1e-10
                chi2 = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + eps))
                
                # Convert to similarity score
                similarity = max(0, 100 - chi2 * 10)
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 100
    
    def _check_shape_consistency(self, images: List[Image.Image]) -> float:
        """Check shape consistency across images (simplified)"""
        
        # Simple edge-based consistency check
        edge_signatures = []
        
        for image in images:
            gray = np.array(image.convert('L'))
            
            # Simple edge detection
            edges = np.abs(np.diff(gray, axis=0)).sum() + np.abs(np.diff(gray, axis=1)).sum()
            edge_density = edges / gray.size
            
            edge_signatures.append(edge_density)
        
        if len(edge_signatures) < 2:
            return 100
        
        # Calculate coefficient of variation (lower is more consistent)
        mean_signature = np.mean(edge_signatures)
        std_signature = np.std(edge_signatures)
        
        if mean_signature > 0:
            cv = std_signature / mean_signature
            consistency = max(0, 100 - cv * 200)  # Scale factor
        else:
            consistency = 100
        
        return consistency
    
    def save_character_profile(self, character_profile: Dict[str, Any], 
                              profile_path: Path):
        """Save character profile to file"""
        
        try:
            with open(profile_path, 'w') as f:
                json.dump(character_profile, f, indent=2)
            
            self.logger.info(f"Saved character profile to {profile_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save character profile: {e}")
            raise
    
    def load_character_profile(self, profile_path: Path) -> Dict[str, Any]:
        """Load character profile from file"""
        
        try:
            with open(profile_path, 'r') as f:
                character_profile = json.load(f)
            
            # Store in memory
            char_id = character_profile['character_id']
            self.character_profiles[char_id] = character_profile
            
            self.logger.info(f"Loaded character profile from {profile_path}")
            return character_profile
            
        except Exception as e:
            self.logger.error(f"Failed to load character profile: {e}")
            raise