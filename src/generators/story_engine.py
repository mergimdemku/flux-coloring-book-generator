"""
Story generation engine for creating coloring book narratives
"""

import random
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class StoryScene:
    """Represents a single scene in the story"""
    scene_number: int
    title: str
    description: str
    setting: str
    action: str
    emotional_tone: str

class StoryEngine:
    """Generates coherent stories for coloring books"""
    
    def __init__(self):
        self.story_templates = {
            'adventure': self._load_adventure_templates(),
            'daily': self._load_daily_templates(),
            'friendship': self._load_friendship_templates(),
            'learning': self._load_learning_templates(),
            'seasonal': self._load_seasonal_templates()
        }
        
    def generate_story(self, theme: str, character_name: str, character_desc: str, 
                      page_count: int, custom_story: str = "") -> List[StoryScene]:
        """Generate a complete story"""
        
        if custom_story:
            return self._generate_custom_story(custom_story, character_name, page_count)
        
        if theme not in self.story_templates:
            theme = 'adventure'  # Default fallback
            
        template = random.choice(self.story_templates[theme])
        return self._expand_template(template, character_name, character_desc, page_count)
    
    def _expand_template(self, template: Dict, character_name: str, 
                        character_desc: str, page_count: int) -> List[StoryScene]:
        """Expand a story template into full scenes"""
        scenes = []
        base_scenes = template['scenes']
        
        # Calculate how many content scenes we need (minus cover pages)
        content_scenes = page_count - 4  # Remove cover, back, and 2 activity pages
        
        # Expand or contract the base scenes to match desired count
        if len(base_scenes) > content_scenes:
            # Select most important scenes
            selected_scenes = base_scenes[:content_scenes]
        else:
            # Expand with variations
            selected_scenes = base_scenes[:]
            while len(selected_scenes) < content_scenes:
                # Add bridging scenes or variations
                base_scene = random.choice(base_scenes)
                variation = self._create_scene_variation(base_scene, len(selected_scenes) + 1)
                selected_scenes.append(variation)
        
        # Convert to StoryScene objects
        for i, scene_data in enumerate(selected_scenes, 1):
            scene = StoryScene(
                scene_number=i,
                title=scene_data['title'].replace('{character}', character_name),
                description=scene_data['description'].replace('{character}', character_name),
                setting=scene_data['setting'],
                action=scene_data['action'].replace('{character}', character_name),
                emotional_tone=scene_data['tone']
            )
            scenes.append(scene)
            
        return scenes
    
    def _create_scene_variation(self, base_scene: Dict, scene_number: int) -> Dict:
        """Create a variation of an existing scene"""
        variations = {
            'settings': ['park', 'garden', 'house', 'street', 'playground', 'kitchen'],
            'actions': ['exploring', 'searching', 'playing', 'resting', 'thinking', 'discovering'],
            'tones': ['curious', 'happy', 'determined', 'surprised', 'content', 'excited']
        }
        
        return {
            'title': f"Scene {scene_number}",
            'description': base_scene['description'],
            'setting': random.choice(variations['settings']),
            'action': random.choice(variations['actions']),
            'tone': random.choice(variations['tones'])
        }
    
    def _generate_custom_story(self, custom_story: str, character_name: str, 
                              page_count: int) -> List[StoryScene]:
        """Generate scenes from custom story description"""
        # Simple approach: split custom story into sentences and create scenes
        sentences = [s.strip() for s in custom_story.split('.') if s.strip()]
        content_scenes = page_count - 4
        
        scenes = []
        
        if not sentences:
            # Fallback to adventure template
            return self.generate_story('adventure', character_name, '', page_count)
        
        # Expand or contract sentences to match scene count
        while len(sentences) < content_scenes:
            # Duplicate and vary sentences
            sentences.extend(sentences[:content_scenes - len(sentences)])
        
        sentences = sentences[:content_scenes]
        
        for i, sentence in enumerate(sentences, 1):
            scene = StoryScene(
                scene_number=i,
                title=f"Scene {i}",
                description=sentence.replace("character", character_name),
                setting="various",
                action=sentence.replace("character", character_name),
                emotional_tone="engaging"
            )
            scenes.append(scene)
            
        return scenes
    
    def _load_adventure_templates(self) -> List[Dict]:
        """Load adventure story templates"""
        return [{
            'title': 'The Great Search',
            'scenes': [
                {
                    'title': '{character} wakes up',
                    'description': '{character} wakes up and notices something important is missing',
                    'setting': 'bedroom',
                    'action': 'waking up and looking around',
                    'tone': 'curious'
                },
                {
                    'title': 'Starting the search',
                    'description': '{character} begins searching in familiar places',
                    'setting': 'house',
                    'action': 'searching and exploring',
                    'tone': 'determined'
                },
                {
                    'title': 'Asking for help',
                    'description': '{character} asks friends or family for help',
                    'setting': 'yard',
                    'action': 'talking and gesturing',
                    'tone': 'hopeful'
                },
                {
                    'title': 'Following clues',
                    'description': '{character} discovers clues that lead to new places',
                    'setting': 'park',
                    'action': 'investigating and following',
                    'tone': 'excited'
                },
                {
                    'title': 'Meeting challenges',
                    'description': '{character} faces small obstacles but keeps going',
                    'setting': 'forest path',
                    'action': 'overcoming and persevering',
                    'tone': 'brave'
                },
                {
                    'title': 'Making a discovery',
                    'description': '{character} finds something unexpected and helpful',
                    'setting': 'clearing',
                    'action': 'discovering and examining',
                    'tone': 'surprised'
                },
                {
                    'title': 'Getting closer',
                    'description': '{character} realizes they are very close to the goal',
                    'setting': 'near destination',
                    'action': 'recognizing and approaching',
                    'tone': 'hopeful'
                },
                {
                    'title': 'Final discovery',
                    'description': '{character} finally finds what they were looking for',
                    'setting': 'special place',
                    'action': 'finding and celebrating',
                    'tone': 'joyful'
                },
                {
                    'title': 'Sharing the joy',
                    'description': '{character} shares their success with friends',
                    'setting': 'home',
                    'action': 'sharing and celebrating together',
                    'tone': 'happy'
                },
                {
                    'title': 'Happy ending',
                    'description': '{character} reflects on the adventure and rests contentedly',
                    'setting': 'comfortable spot',
                    'action': 'resting and reflecting',
                    'tone': 'content'
                }
            ]
        }]
    
    def _load_daily_templates(self) -> List[Dict]:
        """Load daily activities templates"""
        return [{
            'title': 'A Day in the Life',
            'scenes': [
                {
                    'title': 'Morning wake-up',
                    'description': '{character} starts the day with morning routine',
                    'setting': 'bedroom',
                    'action': 'stretching and getting ready',
                    'tone': 'fresh'
                },
                {
                    'title': 'Breakfast time',
                    'description': '{character} enjoys a healthy breakfast',
                    'setting': 'kitchen',
                    'action': 'eating and drinking',
                    'tone': 'satisfied'
                },
                {
                    'title': 'Morning exercise',
                    'description': '{character} goes for a walk or plays outside',
                    'setting': 'outdoors',
                    'action': 'walking and playing',
                    'tone': 'energetic'
                },
                {
                    'title': 'Learning time',
                    'description': '{character} learns something new or practices a skill',
                    'setting': 'study area',
                    'action': 'learning and practicing',
                    'tone': 'focused'
                },
                {
                    'title': 'Helping others',
                    'description': '{character} helps with chores or assists someone',
                    'setting': 'various',
                    'action': 'helping and working',
                    'tone': 'helpful'
                },
                {
                    'title': 'Playtime',
                    'description': '{character} enjoys free play with favorite toys',
                    'setting': 'play area',
                    'action': 'playing and imagining',
                    'tone': 'joyful'
                },
                {
                    'title': 'Afternoon snack',
                    'description': '{character} takes a break for a healthy snack',
                    'setting': 'kitchen',
                    'action': 'eating and resting',
                    'tone': 'peaceful'
                },
                {
                    'title': 'Creative time',
                    'description': '{character} draws, builds, or creates something',
                    'setting': 'art area',
                    'action': 'creating and making',
                    'tone': 'inspired'
                },
                {
                    'title': 'Evening routine',
                    'description': '{character} prepares for bedtime',
                    'setting': 'bathroom',
                    'action': 'washing and preparing',
                    'tone': 'calm'
                },
                {
                    'title': 'Bedtime story',
                    'description': '{character} enjoys a story before sleep',
                    'setting': 'bedroom',
                    'action': 'listening and relaxing',
                    'tone': 'peaceful'
                }
            ]
        }]
    
    def _load_friendship_templates(self) -> List[Dict]:
        """Load friendship story templates"""
        return [{
            'title': 'Making Friends',
            'scenes': [
                {
                    'title': 'Feeling lonely',
                    'description': '{character} wishes for a friend to play with',
                    'setting': 'home',
                    'action': 'looking out window sadly',
                    'tone': 'lonely'
                },
                {
                    'title': 'Going outside',
                    'description': '{character} decides to go out and meet others',
                    'setting': 'doorway',
                    'action': 'stepping outside bravely',
                    'tone': 'hopeful'
                },
                {
                    'title': 'First encounter',
                    'description': '{character} sees someone new but feels shy',
                    'setting': 'park',
                    'action': 'watching from distance',
                    'tone': 'nervous'
                },
                {
                    'title': 'Taking courage',
                    'description': '{character} gathers courage to say hello',
                    'setting': 'playground',
                    'action': 'approaching slowly',
                    'tone': 'brave'
                },
                {
                    'title': 'First words',
                    'description': '{character} introduces themselves',
                    'setting': 'park bench',
                    'action': 'talking and gesturing',
                    'tone': 'friendly'
                },
                {
                    'title': 'Finding common ground',
                    'description': '{character} discovers shared interests',
                    'setting': 'playground',
                    'action': 'pointing and sharing',
                    'tone': 'excited'
                },
                {
                    'title': 'Playing together',
                    'description': '{character} enjoys first games with new friend',
                    'setting': 'play area',
                    'action': 'running and laughing',
                    'tone': 'joyful'
                },
                {
                    'title': 'Helping each other',
                    'description': '{character} and friend help when one has trouble',
                    'setting': 'various',
                    'action': 'assisting and supporting',
                    'tone': 'caring'
                },
                {
                    'title': 'Making plans',
                    'description': '{character} and friend plan to meet again',
                    'setting': 'park exit',
                    'action': 'agreeing and planning',
                    'tone': 'happy'
                },
                {
                    'title': 'Looking forward',
                    'description': '{character} goes home excited about new friendship',
                    'setting': 'home',
                    'action': 'smiling and dreaming',
                    'tone': 'content'
                }
            ]
        }]
    
    def _load_learning_templates(self) -> List[Dict]:
        """Load learning story templates"""
        return [{
            'title': 'Learning Adventure',
            'scenes': [
                {
                    'title': 'New challenge',
                    'description': '{character} encounters something they want to learn',
                    'setting': 'classroom',
                    'action': 'looking and wondering',
                    'tone': 'curious'
                },
                {
                    'title': 'First attempt',
                    'description': '{character} tries something new for the first time',
                    'setting': 'learning space',
                    'action': 'trying and practicing',
                    'tone': 'determined'
                },
                {
                    'title': 'Making mistakes',
                    'description': '{character} makes errors but keeps trying',
                    'setting': 'practice area',
                    'action': 'attempting and adjusting',
                    'tone': 'persistent'
                },
                {
                    'title': 'Getting help',
                    'description': '{character} asks for guidance from a teacher',
                    'setting': 'with mentor',
                    'action': 'asking and listening',
                    'tone': 'open'
                },
                {
                    'title': 'Understanding',
                    'description': '{character} begins to understand the concept',
                    'setting': 'study area',
                    'action': 'thinking and connecting',
                    'tone': 'enlightened'
                },
                {
                    'title': 'More practice',
                    'description': '{character} practices the new skill repeatedly',
                    'setting': 'practice space',
                    'action': 'repeating and improving',
                    'tone': 'focused'
                },
                {
                    'title': 'Small success',
                    'description': '{character} achieves a small breakthrough',
                    'setting': 'learning area',
                    'action': 'succeeding and celebrating',
                    'tone': 'proud'
                },
                {
                    'title': 'Sharing knowledge',
                    'description': '{character} helps someone else learn',
                    'setting': 'with friend',
                    'action': 'teaching and explaining',
                    'tone': 'generous'
                },
                {
                    'title': 'Mastery',
                    'description': '{character} demonstrates their new skill confidently',
                    'setting': 'demonstration area',
                    'action': 'performing skillfully',
                    'tone': 'confident'
                },
                {
                    'title': 'Ready for more',
                    'description': '{character} looks forward to learning something else',
                    'setting': 'looking ahead',
                    'action': 'planning and dreaming',
                    'tone': 'eager'
                }
            ]
        }]
    
    def _load_seasonal_templates(self) -> List[Dict]:
        """Load seasonal activity templates"""
        return [{
            'title': 'Seasonal Fun',
            'scenes': [
                {
                    'title': 'Noticing changes',
                    'description': '{character} notices the season changing',
                    'setting': 'outdoors',
                    'action': 'observing and pointing',
                    'tone': 'aware'
                },
                {
                    'title': 'Preparing for season',
                    'description': '{character} gets ready for seasonal activities',
                    'setting': 'home',
                    'action': 'gathering and preparing',
                    'tone': 'excited'
                },
                {
                    'title': 'Seasonal clothing',
                    'description': '{character} puts on appropriate seasonal wear',
                    'setting': 'bedroom',
                    'action': 'dressing and adjusting',
                    'tone': 'ready'
                },
                {
                    'title': 'First activity',
                    'description': '{character} tries their first seasonal activity',
                    'setting': 'outdoors',
                    'action': 'engaging and exploring',
                    'tone': 'thrilled'
                },
                {
                    'title': 'Seasonal food',
                    'description': '{character} enjoys special seasonal treats',
                    'setting': 'kitchen',
                    'action': 'tasting and savoring',
                    'tone': 'delighted'
                },
                {
                    'title': 'Playing with nature',
                    'description': '{character} interacts with seasonal elements',
                    'setting': 'nature',
                    'action': 'playing and discovering',
                    'tone': 'wonder'
                },
                {
                    'title': 'Seasonal crafts',
                    'description': '{character} makes something with seasonal materials',
                    'setting': 'craft area',
                    'action': 'creating and building',
                    'tone': 'creative'
                },
                {
                    'title': 'Sharing with others',
                    'description': '{character} enjoys seasonal activities with friends',
                    'setting': 'community',
                    'action': 'sharing and playing together',
                    'tone': 'social'
                },
                {
                    'title': 'Seasonal celebration',
                    'description': '{character} participates in seasonal festivities',
                    'setting': 'celebration area',
                    'action': 'celebrating and enjoying',
                    'tone': 'festive'
                },
                {
                    'title': 'Seasonal memories',
                    'description': '{character} reflects on wonderful seasonal experiences',
                    'setting': 'cozy spot',
                    'action': 'remembering and smiling',
                    'tone': 'grateful'
                }
            ]
        }]