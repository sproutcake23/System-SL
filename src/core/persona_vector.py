"""
═══════════════════════════════════════════════════════════════════
  SL - Persona Vector Builder for Task Ranking
═══════════════════════════════════════════════════════════════════
  Loads persona.json and creates semantic vector for task prioritization
  
  Location: src/core/persona_vector.py
"""

import json
import numpy as np
from pathlib import Path


class PersonaVector:
    """Build and use semantic vector from persona data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.persona_file = self.data_dir / "persona.json"
        self.persona_data = None
        self.weighted_blob = None
        self.user_vector = None
        self.model = None
    
    def persona_exists(self):
        """Check if persona file exists"""
        return self.persona_file.exists()
    
    def load_persona(self):
        """Load persona data from JSON"""
        if not self.persona_exists():
            return None
        
        with open(self.persona_file) as f:
            self.persona_data = json.load(f)
        
        return self.persona_data
    
    def build_weighted_blob(self):
        """Create weighted text blob by repeating based on impact"""
        if not self.persona_data:
            self.load_persona()
        
        if not self.persona_data:
            return ""
        
        weighted_text = ""
        
        for response in self.persona_data['responses']:
            answer = response['answer']
            impact = response['impact']
            
            # Repeat answer N times based on impact rating
            # Impact 3 = appears 3 times, Impact 1 = appears once
            weighted_text += (answer + " ") * impact
        
        self.weighted_blob = weighted_text.strip()
        return self.weighted_blob
    
    def create_vector(self, model_name='all-MiniLM-L6-v2'):
        """
        Create semantic vector using sentence-transformers
        
        Args:
            model_name: SentenceTransformer model to use
        
        Returns:
            numpy array: Semantic vector
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            print("⚠️  sentence-transformers not installed!")
            print("   Install: pip install sentence-transformers")
            return None
        
        if not self.weighted_blob:
            self.build_weighted_blob()
        
        if not self.weighted_blob:
            return None
        
        # Load model (cached after first use)
        if not self.model:
            self.model = SentenceTransformer(model_name)
        
        # Create vector
        self.user_vector = self.model.encode(self.weighted_blob)
        
        return self.user_vector
    
    def calculate_task_score(self, task_description):
        """
        Calculate alignment score between task and user profile
        
        Args:
            task_description (str): Task title/description
        
        Returns:
            float: Score from 0-100 (higher = better alignment)
        """
        if not self.user_vector:
            self.create_vector()
        
        if self.user_vector is None:
            # Fallback: return neutral score if no vector
            return 50.0
        
        # Get task vector
        task_vector = self.model.encode(task_description)
        
        # Calculate cosine similarity
        similarity = np.dot(task_vector, self.user_vector) / (
            np.linalg.norm(task_vector) * np.linalg.norm(self.user_vector)
        )
        
        # Scale to 0-100
        score = similarity * 100
        
        return float(score)
    
    def get_priority_tier(self, score):
        """
        Convert score to priority tier
        
        Args:
            score (float): Alignment score
        
        Returns:
            tuple: (tier_symbol, tier_name)
        """
        if score >= 80:
            return "🔴", "CRITICAL"
        elif score >= 65:
            return "🟠", "HIGH"
        elif score >= 50:
            return "🟡", "MEDIUM"
        elif score >= 35:
            return "🟢", "LOW"
        else:
            return "⚪", "MINIMAL"
    
    def rank_tasks(self, tasks_dict):
        """
        Rank all tasks by alignment with user profile
        
        Args:
            tasks_dict (dict): Tasks organized by category
                Example: {"work": [{"title": "Task 1"}, ...], ...}
        
        Returns:
            list: Sorted list of (category, task, score, tier) tuples
        """
        if not self.persona_exists():
            # Return tasks unranked if no persona
            unranked = []
            for category, tasks in tasks_dict.items():
                for task in tasks:
                    unranked.append((category, task, 50.0, ("🟡", "UNRANKED")))
            return unranked
        
        # Calculate scores for all tasks
        scored_tasks = []
        
        for category, tasks in tasks_dict.items():
            for task in tasks:
                title = task.get("title", "")
                score = self.calculate_task_score(title)
                tier = self.get_priority_tier(score)
                
                scored_tasks.append((category, task, score, tier))
        
        # Sort by score (highest first)
        scored_tasks.sort(key=lambda x: x[2], reverse=True)
        
        return scored_tasks


# ═══════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════════════

def example_usage():
    """Example: How to use PersonaVector in your task management"""
    
    # Initialize
    persona_vec = PersonaVector()
    
    # Check if persona exists
    if not persona_vec.persona_exists():
        print("⚠️  No persona found. Run onboarding first.")
        return
    
    # Load and build vector
    persona_vec.load_persona()
    persona_vec.build_weighted_blob()
    persona_vec.create_vector()
    
    # Example tasks
    tasks = {
        "work": [
            {"title": "Refactor Python API backend", "deadline": "2025-03-01"},
            {"title": "Write documentation for new features", "deadline": "2025-03-05"},
        ],
        "personal": [
            {"title": "Go grocery shopping", "deadline": None},
            {"title": "Study machine learning algorithms", "deadline": "2025-03-03"},
        ],
        "chores": [
            {"title": "Clean apartment", "deadline": None},
        ]
    }
    
    # Rank tasks
    ranked = persona_vec.rank_tasks(tasks)
    
    # Display
    print("\n📊 Tasks Ranked by Semantic Alignment:\n")
    print(f"{'Tier':<12} {'Score':<8} {'Category':<12} {'Task'}")
    print("─" * 70)
    
    for category, task, score, (symbol, tier_name) in ranked:
        title = task["title"]
        print(f"{symbol} {tier_name:<8} {score:<8.1f} {category:<12} {title}")
    
    print()


def get_task_priority_display(task_title, persona_vec=None):
    """
    Helper: Get priority display for a single task
    
    Args:
        task_title (str): Task description
        persona_vec (PersonaVector): Optional pre-initialized vector
    
    Returns:
        str: Formatted priority display (e.g., "🔴 87.3")
    """
    if persona_vec is None:
        persona_vec = PersonaVector()
        if not persona_vec.persona_exists():
            return "🟡 --.-"  # No persona, return neutral
        persona_vec.create_vector()
    
    score = persona_vec.calculate_task_score(task_title)
    symbol, _ = persona_vec.get_priority_tier(score)
    
    return f"{symbol} {score:.1f}"


# For testing
if __name__ == "__main__":
    example_usage()
