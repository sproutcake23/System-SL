"""
═══════════════════════════════════════════════════════════════════
  SL - First-Time Onboarding & Persona Builder
═══════════════════════════════════════════════════════════════════
  Runs automatically when user launches SL for the first time
  Collects semantic profile for intelligent task prioritization
  
"""

import json
import os
from pathlib import Path
from datetime import datetime


class PersonaOnboarding:
    """First-time setup wizard for collecting user's semantic profile"""
    
    def __init__(self):
      # Use data directory for storing user data
        prog_name = "system-sl"

        if os.name == 'nt':
            # Windows: AppData/Roaming/system-sl
            base_dir = Path(os.environ.get('APPDATA', Path.home() / "AppData" / "Roaming"))
            self.data_dir = base_dir / prog_name
        else:
            # Linux: ~/.config/system-sl
            self.data_dir = Path.home() / ".config" / prog_name
                            
            self.persona_file = self.data_dir / "persona.json"
            self.setup_flag = self.data_dir / ".setup_complete"
            
                   
              ``                  
        self.questions = [
            {
                "id": 1,
                "category": "IDENTITY",
                "question": "What is your ultimate career or life ambition?",
                "hint": "e.g., Senior AI Engineer, Product Manager, Startup Founder",
            },
            {
                "id": 2,
                "category": "ACADEMIC",
                "question": "What subjects or fields are you studying/interested in?",
                "hint": "e.g., Computer Science, Mathematics, Data Science",
            },
            {
                "id": 3,
                "category": "SKILLS",
                "question": "What technical skills, tools, or languages are you focusing on?",
                "hint": "e.g., Python, Docker, React, AWS, TensorFlow",
            },
            {
                "id": 4,
                "category": "ACTIONS",
                "question": "What actions do you want to spend most of your time doing?",
                "hint": "e.g., Coding, designing, writing, researching",
            },
            {
                "id": 5,
                "category": "PROJECTS",
                "question": "What kind of projects do you love building?",
                "hint": "e.g., Web apps, ML models, APIs, mobile apps",
            },
            {
                "id": 6,
                "category": "MILESTONE",
                "question": "What is your main objective for the next 3-6 months?",
                "hint": "e.g., Land internship, build portfolio, launch product",
            },
            {
                "id": 7,
                "category": "COGNITION",
                "question": "What types of problems do you enjoy solving most?",
                "hint": "e.g., Algorithms, system design, optimization",
            },
            {
                "id": 8,
                "category": "HABITS",
                "question": "What daily habits are essential to your growth?",
                "hint": "e.g., Reading, gym, meditation, learning",
            },
            {
                "id": 9,
                "category": "INDUSTRY",
                "question": "Which industries do you want your work to impact?",
                "hint": "e.g., AI, FinTech, Healthcare, Climate Tech",
            },
            {
                "id": 10,
                "category": "VALUES",
                "question": "What keywords describe your core professional values?",
                "hint": "e.g., Efficient, innovative, scalable, quality",
            }
        ]
        
        self.responses = []
    
    def is_first_time(self):
        """Check if this is the first time running SL"""
        return not self.setup_flag.exists()
    
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def display_welcome(self):
        """Show welcome screen with Solo Leveling theme"""
        print("\n" + "═" * 70)
        print("  ⚔️  THE SYSTEM AWAKENS")
        print("═" * 70)
        print("""
    "Arise, Player."
    
    🎯 Before you begin your journey, the SYSTEM must understand
       who you are and what you seek to achieve.
    
    📋 The SYSTEM will ask you 10 questions to build your Player Profile.
       This profile will help prioritize quests aligned with YOUR goals.
    
    ⏱️  Time Required: 3-5 minutes
    💡 Answer with KEYWORDS, not sentences
    ⚡ Rate each answer's IMPACT on your journey (1-3)
        """)
        print("═" * 70)
        
        response = input("\n🎮 Ready to begin character creation? (yes/skip): ").strip().lower()
        
        if response in ['skip', 's', 'n', 'no']:
            return False
        
        return True
    
    def display_question(self, q):
        """Display a single question with Solo Leveling theme"""
        print(f"\n{'─' * 70}")
        print(f"⚔️  QUEST {q['id']}/10 - {q['category']}")
        print(f"{'─' * 70}")
        print(f"\n❓ {q['question']}")
        print(f"💡 Example: {q['hint']}")
    
    def get_answer(self):
        """Get and validate answer"""
        while True:
            answer = input("\n✍️  Your Answer: ").strip().lower()
            
            if not answer:
                print("   ⚠️  The SYSTEM requires an answer.")
                continue
            
            if len(answer) < 3:
                print("   ⚠️  Answer too short. Provide meaningful keywords.")
                continue
            
            return answer
    
    def get_impact(self):
        """Get and validate impact rating"""
        print("\n⚡ Impact Level:")
        print("   1 = Low     (peripheral interest)")
        print("   2 = Medium  (important focus)")
        print("   3 = High    (core identity - CRITICAL)")
        
        while True:
            try:
                rating = input("\n🎯 Impact (1/2/3): ").strip()
                impact = int(rating)
                
                if impact in [1, 2, 3]:
                    labels = {1: "🟢 Low", 2: "🟡 Medium", 3: "🔴 High"}
                    print(f"   ✓ {labels[impact]} Impact Recorded")
                    return impact
                
                print("   ⚠️  Invalid. Enter 1, 2, or 3")
                
            except ValueError:
                print("   ⚠️  Invalid input. Enter a number (1, 2, or 3)")
    
    def run_onboarding(self):
        """Execute the onboarding questionnaire"""
        for q in self.questions:
            self.display_question(q)
            answer = self.get_answer()
            impact = self.get_impact()
            
            self.responses.append({
                "question_id": q['id'],
                "category": q['category'],
                "question": q['question'],
                "answer": answer,
                "impact": impact
            })
            
            # Progress with XP bar theme
            progress = (q['id'] / len(self.questions)) * 100
            filled = int(progress / 5)
            bar = "█" * filled + "░" * (20 - filled)
            print(f"\n📊 Profile Completion: [{bar}] {progress:.0f}%")
    
    def save_persona(self):
        """Save persona data to data directory"""
        self.ensure_data_dir()
        
        stats = {
            "high_count": sum(1 for r in self.responses if r['impact'] == 3),
            "medium_count": sum(1 for r in self.responses if r['impact'] == 2),
            "low_count": sum(1 for r in self.responses if r['impact'] == 1)
        }
        
        persona_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "player_name": os.getenv("USER", "Player"),
            "responses": self.responses,
            "statistics": stats
        }
        
        with open(self.persona_file, 'w') as f:
            json.dump(persona_data, f, indent=2)
        
        # Create setup complete flag
        self.setup_flag.touch()
    
    def display_completion(self):
        """Show completion message with Solo Leveling theme"""
        stats = {
            "high": sum(1 for r in self.responses if r['impact'] == 3),
            "medium": sum(1 for r in self.responses if r['impact'] == 2),
            "low": sum(1 for r in self.responses if r['impact'] == 3)
        }
        
        print("\n" + "═" * 70)
        print("✨ PLAYER PROFILE CREATED ✨")
        print("═" * 70)
        print("""
    "The System has acknowledged your potential."
        """)
        print(f"📊 Your Attribute Distribution:")
        print(f"   🔴 Core Attributes:       {stats['high']} (High Priority)")
        print(f"   🟡 Secondary Attributes:  {stats['medium']} (Medium Priority)")
        print(f"   🟢 Support Attributes:    {stats['low']} (Low Priority)")
        print(f"\n💾 Profile saved to: {self.persona_file}")
        print("""
    🎮 The SYSTEM will now prioritize quests based on your profile.
       Tasks aligned with your Core Attributes will rank highest.
        """)
        print("═" * 70)
        print("\n⚔️  You may now begin your journey.\n")
    
    def skip_setup(self):
        """Handle skipped setup"""
        self.ensure_data_dir()
        
        print("\n⚠️  Profile creation skipped.")
        print("   You can create your profile later with: (ep) Edit Profile")
        print("   Tasks will use default prioritization until then.\n")
        
        # Create flag but no persona
        self.setup_flag.touch()
    
    def run(self):
        """Main onboarding flow"""
        try:
            if self.display_welcome():
                self.run_onboarding()
                self.save_persona()
                self.display_completion()
                return True
            else:
                self.skip_setup()
                return False
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Profile creation interrupted.")
            print("   Run SL again to complete setup.\n")
            return False
        
        except Exception as e:
            print(f"\n❌ Error during setup: {e}")
            print("   Please report this issue.\n")
            return False


def check_and_run_onboarding():
    """
    Check if onboarding is needed and run it.
    Call this from main.py before showing the main menu.
    
    Returns:
        bool: True if setup was completed/already done, False if skipped
    """
    onboarding = PersonaOnboarding()
    
    if onboarding.is_first_time():
        return onboarding.run()
    
    return True  # Already set up


def force_run_setup():
    """
    Force run setup (for Edit Profile command).
    
    Returns:
        bool: True if completed, False if cancelled
    """
    onboarding = PersonaOnboarding()
    
    if not onboarding.is_first_time():
        print("\n⚠️  Player Profile already exists.")
        response = input("Recreate your profile? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("   Cancelled.\n")
            return False
    
    return onboarding.run()



