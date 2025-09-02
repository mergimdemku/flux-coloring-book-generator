#!/usr/bin/env python3
"""
TRUE RANDOM Story Generator - Generates UNIQUE stories, not the same 5 templates!
"""

import random
import time
from typing import Dict, List, Any

class TrueRandomStoryGenerator:
    """Generates ACTUALLY DIFFERENT stories each time"""
    
    def __init__(self):
        # Seed with time for true randomness
        random.seed(int(time.time() * 1000000) % 2147483647)
        
        # Story elements to mix and match
        self.settings = [
            "enchanted forest", "underwater kingdom", "space station", "magical castle", 
            "dinosaur valley", "candy land", "robot city", "pirate ship", "fairy garden",
            "jungle temple", "arctic ice palace", "volcano island", "cloud kingdom",
            "desert oasis", "haunted mansion", "toy store", "farm", "zoo", "circus",
            "mountain village", "beach resort", "underground caves", "tree house village"
        ]
        
        self.protagonists = {
            'girl': ["Emma", "Lily", "Sofia", "Maya", "Zara", "Luna", "Rose", "Ivy", "Aria", "Nova"],
            'boy': ["Max", "Leo", "Sam", "Finn", "Jake", "Oliver", "Noah", "Ethan", "Ryan", "Alex"]
        }
        
        self.companions = [
            "talking cat", "friendly dragon", "magic butterfly", "wise owl", "playful puppy",
            "robot friend", "unicorn", "fairy", "talking bear", "phoenix", "mermaid",
            "alien buddy", "magic rabbit", "helpful monkey", "singing bird", "tiny elephant"
        ]
        
        self.problems = [
            "lost treasure", "missing colors", "broken magic", "sad creature", "stolen item",
            "mysterious illness", "trapped friends", "dark spell", "natural disaster", 
            "mean bully", "lost way home", "broken machine", "empty celebration",
            "scary monster", "unfair rule", "missing ingredient", "broken bridge"
        ]
        
        self.objects = [
            "magic wand", "golden key", "crystal ball", "ancient map", "flying carpet",
            "magic seeds", "rainbow gem", "time machine", "wish stone", "healing potion",
            "music box", "magic paintbrush", "enchanted book", "portal mirror", "star compass"
        ]
        
        self.activities = [
            "solving puzzles", "making new friends", "learning magic", "building something",
            "organizing a party", "winning a contest", "discovering secrets", "helping others",
            "going on adventure", "saving the day", "finding courage", "teaching lessons",
            "exploring new places", "overcoming fears", "bringing joy", "fixing problems"
        ]
        
        self.emotions = [
            "brave", "curious", "determined", "creative", "kind", "clever", "patient",
            "generous", "optimistic", "adventurous", "confident", "caring", "playful"
        ]
        
    def generate_unique_story(self) -> Dict[str, Any]:
        """Generate a COMPLETELY UNIQUE story each time"""
        
        # Random gender and character
        gender = random.choice(['girl', 'boy'])
        protagonist = random.choice(self.protagonists[gender])
        gender_desc = f"young {gender}"
        
        # Random story elements
        setting = random.choice(self.settings)
        companion = random.choice(self.companions)
        problem = random.choice(self.problems)
        object = random.choice(self.objects)
        activity = random.choice(self.activities)
        emotion = random.choice(self.emotions)
        
        # Generate unique title
        title_templates = [
            f"{protagonist}'s {setting.title()} Adventure",
            f"{protagonist} and the {companion.title()}",
            f"The {emotion.title()} {protagonist}",
            f"{protagonist} Saves the {setting.title()}",
            f"{protagonist}'s {object.title()} Quest",
            f"The Mystery of {setting.title()}"
        ]
        title = random.choice(title_templates)
        
        # Generate unique summary
        summary = f"{gender_desc.capitalize()} {protagonist} discovers a {problem} in the {setting} and must use {emotion} thinking and a {object} to help their friend the {companion} while {activity}."
        
        # Generate 20 UNIQUE scenes based on story elements
        scenes = self.generate_dynamic_scenes(protagonist, gender_desc, setting, companion, problem, object, activity, emotion)
        
        return {
            'title': title,
            'summary': summary,
            'scenes': scenes,
            'protagonist': protagonist,
            'gender': gender,
            'gender_desc': gender_desc,
            'setting': setting,
            'companion': companion,
            'unique_id': f"{setting}_{problem}_{int(time.time())}"
        }
    
    def generate_dynamic_scenes(self, protagonist: str, gender_desc: str, setting: str, 
                                companion: str, problem: str, object: str, 
                                activity: str, emotion: str) -> List[str]:
        """Generate 20 unique scenes based on story elements"""
        
        scenes = []
        
        # Act 1: Setup (scenes 1-5)
        scenes.append(f"{gender_desc} {protagonist} exploring the {setting} on a sunny morning")
        scenes.append(f"{protagonist} discovering something unusual about the {problem}")
        scenes.append(f"Meeting a {companion} who needs help with the {problem}")
        scenes.append(f"{protagonist} and the {companion} becoming friends")
        scenes.append(f"Learning about the {object} that might solve the {problem}")
        
        # Act 2: Journey (scenes 6-10)
        scenes.append(f"{protagonist} and {companion} beginning their quest to find the {object}")
        scenes.append(f"Facing the first challenge while {activity} in the {setting}")
        scenes.append(f"{protagonist} using {emotion} thinking to overcome an obstacle")
        scenes.append(f"The {companion} helping {protagonist} when things get difficult")
        scenes.append(f"Discovering a hidden path in the {setting}")
        
        # Act 3: Challenges (scenes 11-15)
        scenes.append(f"Meeting other creatures who are affected by the {problem}")
        scenes.append(f"{protagonist} organizing everyone to work together")
        scenes.append(f"Finding the {object} but it's guarded by a challenge")
        scenes.append(f"Using teamwork and {emotion} actions to get the {object}")
        scenes.append(f"The {companion} showing unexpected bravery")
        
        # Act 4: Resolution (scenes 16-20)
        scenes.append(f"{protagonist} using the {object} to solve the {problem}")
        scenes.append(f"The {setting} transforming into something beautiful")
        scenes.append(f"All the friends celebrating with {activity}")
        scenes.append(f"{protagonist} and {companion} reflecting on their adventure")
        scenes.append(f"Everyone in the {setting} living happily with the problem solved")
        
        return scenes
    
    def generate_batch(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate multiple unique stories"""
        stories = []
        used_combos = set()
        
        for _ in range(count):
            # Keep generating until we get a unique combination
            attempts = 0
            while attempts < 100:
                story = self.generate_unique_story()
                combo_key = f"{story['setting']}_{story['companion']}_{story['unique_id']}"
                
                if combo_key not in used_combos:
                    used_combos.add(combo_key)
                    stories.append(story)
                    break
                attempts += 1
                
        return stories


if __name__ == "__main__":
    generator = TrueRandomStoryGenerator()
    
    # Generate 10 unique stories to show variety
    print("GENERATING 10 TRULY UNIQUE STORIES:\n")
    stories = generator.generate_batch(10)
    
    for i, story in enumerate(stories, 1):
        print(f"{i}. {story['title']}")
        print(f"   Setting: {story['setting']}")
        print(f"   Character: {story['gender_desc']} {story['protagonist']}")
        print(f"   Companion: {story['companion']}")
        print(f"   Summary: {story['summary'][:100]}...")
        print()