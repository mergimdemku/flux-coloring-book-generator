"""
Prompt builder for generating FLUX prompts for coloring book pages
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from .story_engine import StoryScene

@dataclass
class PromptConfig:
    """Configuration for prompt generation"""
    base_style: str
    character_card: str
    negative_prompt: str
    art_style: str
    complexity_level: str

class PromptBuilder:
    """Builds optimized prompts for FLUX image generation"""
    
    def __init__(self):
        self.age_complexity = {
            '2-4 years': 'very simple shapes, minimal details, thick outlines',
            '3-6 years': 'simple clear shapes, moderate details, bold outlines', 
            '5-8 years': 'detailed scenes, fine outlines, multiple objects',
            '6-10 years': 'complex scenes, intricate details, varied line weights'
        }
        
        self.base_coloring_style = (
            "black and white line drawing, coloring book page, "
            "bold clean black outlines only, no shading, no gray, "
            "pure white background, simple line art, thick lines, "
            "high contrast, minimal detail, vector style, "
            "center composition, kid-friendly, monochrome outline"
        )
        
        self.negative_prompt = (
            "color, grayscale shading, gradients, text, watermarks, signature, "
            "background clutter, tiny details, crosshatching, realistic photo, "
            "complex shadows, blurred lines, faded colors, adults only content"
        )
    
    def create_character_card(self, name: str, description: str) -> str:
        """Create a character consistency card"""
        return f"{name}: {description}, same character design throughout, consistent appearance"
    
    def build_scene_prompt(self, scene: StoryScene, character_card: str, 
                          age_range: str, page_type: str = "scene") -> Dict[str, str]:
        """Build a complete prompt for a story scene"""
        
        # Get complexity level for age
        complexity = self.age_complexity.get(age_range, self.age_complexity['3-6 years'])
        
        # Build main prompt
        if page_type == "cover":
            main_prompt = self._build_cover_prompt(scene, character_card, complexity)
        elif page_type == "activity":
            main_prompt = self._build_activity_prompt(scene, character_card, complexity)
        else:
            main_prompt = self._build_scene_prompt(scene, character_card, complexity)
        
        return {
            'prompt': main_prompt,
            'negative_prompt': self.negative_prompt,
            'scene_info': {
                'scene_number': scene.scene_number,
                'title': scene.title,
                'description': scene.description,
                'setting': scene.setting,
                'tone': scene.emotional_tone
            }
        }
    
    def _build_scene_prompt(self, scene: StoryScene, character_card: str, complexity: str) -> str:
        """Build prompt for a regular story scene"""
        
        # Setting-based environment additions
        environment_details = self._get_environment_details(scene.setting)
        
        # Emotion-based scene modifiers
        emotion_modifiers = self._get_emotion_modifiers(scene.emotional_tone)
        
        prompt_parts = [
            self.base_coloring_style,
            character_card,
            f"scene: {scene.description}",
            f"setting: {environment_details}",
            f"mood: {emotion_modifiers}",
            complexity,
            "centered composition",
            "perfect for coloring"
        ]
        
        return ", ".join(prompt_parts)
    
    def _build_cover_prompt(self, scene: StoryScene, character_card: str, complexity: str) -> str:
        """Build prompt for book cover"""
        prompt_parts = [
            "children's coloring book cover page",
            self.base_coloring_style,
            character_card,
            "main character prominently featured",
            "title area at top (blank for text overlay)",
            "decorative border elements",
            complexity,
            "engaging and inviting composition"
        ]
        
        return ", ".join(prompt_parts)
    
    def _build_activity_prompt(self, scene: StoryScene, character_card: str, complexity: str) -> str:
        """Build prompt for activity pages"""
        activities = [
            "simple maze with clear paths",
            "connect the dots puzzle", 
            "counting objects exercise",
            "pattern matching game",
            "find the differences",
            "tracing practice lines"
        ]
        
        activity_type = activities[scene.scene_number % len(activities)]
        
        prompt_parts = [
            f"children's activity page: {activity_type}",
            self.base_coloring_style,
            character_card,
            "educational and fun",
            "clear instructions through visual cues",
            complexity,
            "interactive elements"
        ]
        
        return ", ".join(prompt_parts)
    
    def _get_environment_details(self, setting: str) -> str:
        """Get detailed environment description for setting"""
        environment_map = {
            'bedroom': 'cozy bedroom with bed, toys, window',
            'kitchen': 'friendly kitchen with table, chairs, simple appliances',
            'house': 'comfortable home interior with furniture',
            'yard': 'safe backyard with grass, fence, maybe trees',
            'park': 'public park with trees, paths, playground equipment',
            'playground': 'children\'s playground with swings, slides, sandbox',
            'forest': 'friendly forest with trees, flowers, safe paths',
            'garden': 'beautiful garden with flowers, plants, paths',
            'street': 'quiet neighborhood street with houses, sidewalks',
            'outdoors': 'pleasant outdoor setting with nature elements',
            'various': 'appropriate background setting',
            'nature': 'natural outdoor environment',
            'home': 'comfortable indoor home setting',
            'classroom': 'friendly classroom with desks, learning materials',
            'study area': 'quiet study space with books, supplies'
        }
        
        return environment_map.get(setting, 'simple appropriate background')
    
    def _get_emotion_modifiers(self, emotional_tone: str) -> str:
        """Get visual modifiers based on emotional tone"""
        emotion_map = {
            'curious': 'character looking interested, head tilted, exploring pose',
            'happy': 'character smiling, upbeat posture, positive body language',
            'determined': 'character focused, confident stance, goal-oriented pose',
            'surprised': 'character with wide eyes, alert posture, discovery pose',
            'content': 'character relaxed, peaceful expression, comfortable pose',
            'excited': 'character energetic, animated posture, enthusiastic pose',
            'hopeful': 'character looking forward, optimistic expression, anticipatory pose',
            'brave': 'character confident, strong posture, courageous stance',
            'joyful': 'character very happy, celebratory pose, triumphant expression',
            'peaceful': 'character calm, serene expression, restful pose',
            'friendly': 'character welcoming, open posture, approachable expression',
            'focused': 'character concentrating, attentive pose, engaged expression',
            'helpful': 'character offering assistance, caring posture, kind expression',
            'proud': 'character confident, accomplished expression, successful pose',
            'caring': 'character gentle, nurturing pose, compassionate expression',
            'eager': 'character enthusiastic, ready posture, anticipatory expression'
        }
        
        return emotion_map.get(emotional_tone, 'character with appropriate expression')
    
    def create_consistency_seed_prompt(self, base_prompt: str, character_name: str) -> str:
        """Create a prompt optimized for character consistency using seeds"""
        consistency_additions = [
            f"consistent {character_name} character design",
            "same proportions and features as reference",
            "identical character appearance", 
            "maintain character model throughout"
        ]
        
        return base_prompt + ", " + ", ".join(consistency_additions)
    
    def get_post_processing_instructions(self, age_range: str) -> Dict[str, Any]:
        """Get post-processing parameters based on age range"""
        
        line_thickness_map = {
            '2-4 years': {'min_thickness': 4, 'dilate_kernel': 3},
            '3-6 years': {'min_thickness': 3, 'dilate_kernel': 2}, 
            '5-8 years': {'min_thickness': 2, 'dilate_kernel': 1},
            '6-10 years': {'min_thickness': 2, 'dilate_kernel': 1}
        }
        
        params = line_thickness_map.get(age_range, line_thickness_map['3-6 years'])
        
        return {
            'threshold_method': 'adaptive',
            'line_thickness': params['min_thickness'],
            'morphology_kernel': params['dilate_kernel'],
            'noise_removal': True,
            'contrast_enhancement': True,
            'white_background': True
        }
    
    def build_batch_prompts(self, scenes: List[StoryScene], character_card: str, 
                           age_range: str, book_title: str) -> List[Dict[str, Any]]:
        """Build prompts for all scenes in a story"""
        prompts = []
        
        # Cover page
        cover_scene = StoryScene(0, f"{book_title} Cover", f"Cover page for {book_title}", 
                               "cover", "title presentation", "inviting")
        cover_prompt = self.build_scene_prompt(cover_scene, character_card, age_range, "cover")
        cover_prompt['page_type'] = 'cover'
        prompts.append(cover_prompt)
        
        # Story scenes
        for scene in scenes:
            scene_prompt = self.build_scene_prompt(scene, character_card, age_range, "scene")
            scene_prompt['page_type'] = 'scene'
            prompts.append(scene_prompt)
        
        # Activity pages (2 pages)
        for i in range(2):
            activity_scene = StoryScene(i+100, f"Activity {i+1}", f"Fun activity page {i+1}", 
                                      "activity", "learning and fun", "engaging")
            activity_prompt = self.build_scene_prompt(activity_scene, character_card, age_range, "activity")
            activity_prompt['page_type'] = 'activity'
            prompts.append(activity_prompt)
        
        # Back cover
        back_scene = StoryScene(999, "Back Cover", "Back cover with branding", 
                              "back", "conclusion", "satisfied")
        back_prompt = self.build_scene_prompt(back_scene, character_card, age_range, "cover")
        back_prompt['page_type'] = 'back_cover'
        prompts.append(back_prompt)
        
        return prompts