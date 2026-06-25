"""
═══════════════════════════════════════════════════════════════════
  SL - First-Time Onboarding & Persona Builder
═══════════════════════════════════════════════════════════════════
  Runs automatically when user launches SL for the first time
  Collects semantic profile for intelligent task prioritization

"""

"""Module for handling first-time onboarding and semantic profile generation using SOLID principles."""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional


# =====================================================================
# 0. SHARED CONFIGURATION (single source of truth for both frontends)
# =====================================================================

# The onboarding questionnaire. Shared by the CLI flow
# (PersonaOnboardingEngine) and the GUI flow (OnboardingWindow) so the two
# never drift apart.
ONBOARDING_QUESTIONS: List[Dict[str, Any]] = [
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
    },
]


# =====================================================================
# 1. STORAGE LAYER (Single Responsibility: File System I/O)
# =====================================================================


class PersonaStorageHandler:
    """Manages the storage lifecycle, tracking flags, and serialization of user persona data."""

    def __init__(self, application_name: str = "system-sl") -> None:
        """Initializes storage directories based on the host Operating System.

        Args:
            application_name (str): Directory name where configurations are cached. Defaults to "system-sl".
        """
        if os.name == "nt":
            base_dir: Path = Path(
                os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            )
            self.data_dir: Path = base_dir / application_name
        else:
            self.data_dir: Path = Path.home() / ".config" / application_name

        self.persona_file: Path = self.data_dir / "persona.json"
        self.setup_flag: Path = self.data_dir / ".setup_complete"

    def is_first_time(self) -> bool:
        """Determines if the onboarding process has been executed previously.

        Returns:
            bool: True if the setup complete flag file is missing, otherwise False.
        """
        return not self.setup_flag.exists()

    def ensure_data_directory(self) -> None:
        """Ensures the application data directories are physically allocated on disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def write_persona_profile(
        self, responses: List[Dict[str, Any]], statistics: Dict[str, int]
    ) -> None:
        """Serializes player profiles and saves them as a structured JSON file.

        Args:
            responses (List[Dict[str, Any]]): Collected list of question dictionaries with user answers.
            statistics (Dict[str, int]): Priority tier counts calculated from the survey metrics.
        """
        self.ensure_data_directory()

        persona_data: Dict[str, Any] = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "player_name": os.getenv("USER", "Player"),
            "responses": responses,
            "statistics": statistics,
        }

        with open(self.persona_file, "w") as file_pointer:
            json.dump(persona_data, file_pointer, indent=2)

        self.setup_flag.touch()

    def touch_setup_flag_only(self) -> None:
        """Marks setup execution complete without persisting profile configuration files."""
        self.ensure_data_directory()
        self.setup_flag.touch()


# =====================================================================
# 2. USER INTERFACE LAYER (Single Responsibility: Terminal UI & Validations)
# =====================================================================


class SoloLevelingConsoleUI:
    """Handles terminal layouts, interactive prompt parsing, and input constraints with an RPG flavor."""

    def display_welcome_screen(self) -> bool:
        """Renders the game-themed onboarding introductory prompt.

        Returns:
            bool: True if the user elects to initiate configuration, False if skipped.
        """
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

        response: str = (
            input("\n🎮 Ready to begin character creation? (yes/skip): ")
            .strip()
            .lower()
        )
        return response not in ["skip", "s", "n", "no"]

    def display_question_card(self, question_metadata: Dict[str, Any]) -> None:
        """Renders stylized quest components for individual profile parameters.

        Args:
            question_metadata (Dict[str, Any]): Map describing ID, category, problem string, and input helper context.
        """
        print(f"\n{'─' * 70}")
        print(
            f"⚔️  QUEST {question_metadata['id']}/10 - {question_metadata['category']}"
        )
        print(f"{'─' * 70}")
        print(f"\n❓ {question_metadata['question']}")
        print(f"💡 Example: {question_metadata['hint']}")

    def read_valid_answer(self) -> str:
        """Captures alphanumeric strings from stdin ensuring baseline input requirements are met.

        Returns:
            str: Normalized lower-case alphanumeric keyword text.
        """
        while True:
            answer: str = input("\n✍️  Your Answer: ").strip().lower()

            if not answer:
                print("   ⚠️  The SYSTEM requires an answer.")
                continue

            if len(answer) < 3:
                print("   ⚠️  Answer too short. Provide meaningful keywords.")
                continue

            return answer

    def read_valid_impact_rating(self) -> int:
        """Captures scalar integer importance tiers checking numerical compliance constraints.

        Returns:
            int: Discrete classification ranking bounded inside [1, 3].
        """
        print("\n⚡ Impact Level:")
        print("   1 = Low     (peripheral interest)")
        print("   2 = Medium  (important focus)")
        print("   3 = High    (core identity - CRITICAL)")

        while True:
            try:
                rating: str = input("\n🎯 Impact (1/2/3): ").strip()
                impact: int = int(rating)

                if impact in [1, 2, 3]:
                    labels: Dict[int, str] = {1: "🟢 Low", 2: "🟡 Medium", 3: "🔴 High"}
                    print(f"   ✓ {labels[impact]} Impact Recorded")
                    return impact

                print("   ⚠️  Invalid. Enter 1, 2, or 3")

            except ValueError:
                print("   ⚠️  Invalid input. Enter a number (1, 2, or 3)")

    def render_progress_bar(self, current_step: int, total_steps: int) -> None:
        """Outputs an interactive ASCII progress metric representing survey tracking state.

        Args:
            current_step (int): Index offset of questions resolved.
            total_steps (int): Total length threshold of items managed.
        """
        progress: float = (current_step / total_steps) * 100
        filled: int = int(progress / 5)
        bar: str = "█" * filled + "░" * (20 - filled)
        print(f"\n📊 Profile Completion: [{bar}] {progress:.0f}%")

    def display_completion_screen(
        self,
        high_priority_count: int,
        medium_priority_count: int,
        low_priority_count: int,
        target_file_path: Path,
    ) -> None:
        """Displays finalized classification statistics along with target persistence addresses.

        Args:
            high_priority_count (int): Aggregated metric of high-impact attributes.
            medium_priority_count (int): Aggregated metric of medium-impact attributes.
            low_priority_count (int): Aggregated metric of low-impact attributes.
            target_file_path (Path): Reference path mapping where the profile metadata was written.
        """
        print("\n" + "═" * 70)
        print("✨ PLAYER PROFILE CREATED ✨")
        print("═" * 70)
        print("""
    "The System has acknowledged your potential."
        """)
        print(f"📊 Your Attribute Distribution:")
        print(f"   🔴 Core Attributes:       {high_priority_count} (High Priority)")
        print(f"   🟡 Secondary Attributes:  {medium_priority_count} (Medium Priority)")
        print(f"   🟢 Support Attributes:    {low_priority_count} (Low Priority)")
        print(f"\n💾 Profile saved to: {target_file_path}")
        print("""
    ... The SYSTEM will now prioritize quests based on your profile.
       Tasks aligned with your Core Attributes will rank highest.
        """)
        print("═" * 70)
        print("\n⚔️  You may now begin your journey.\n")

    def display_skip_notification(self) -> None:
        """Renders information feedback notifications tracking initialization skip commands."""
        print("\n⚠️  Profile creation skipped.")
        print("   You can create your profile later with: (ep) Edit Profile")
        print("   Tasks will use default prioritization until then.\n")

    def prompt_profile_recreation(self) -> bool:
        """Requests explicit interactive confirmation regarding mutating existing configuration assets.

        Returns:
            bool: True if overwriting validation holds valid clearance, otherwise False.
        """
        print("\n⚠️  Player Profile already exists.")
        response: str = input("Recreate your profile? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("   Cancelled.\n")
            return False
        return True


# =====================================================================
# 3. CORE SERVICE ORCHESTRATION LAYER (Single Responsibility: Workflow Control)
# =====================================================================


class PersonaOnboardingEngine:
    """Orchestrates configuration data paths combining interfaces for UI views and persistence layers."""

    def __init__(
        self,
        storage_handler: Optional[PersonaStorageHandler] = None,
        user_interface: Optional[SoloLevelingConsoleUI] = None,
    ) -> None:
        """Links interface dependencies tracking user preferences and data management.

        Args:
            storage_handler (Optional[PersonaStorageHandler]): I/O driver resolving data files.
            user_interface (Optional[SoloLevelingConsoleUI]): I/O manager processing human interface steps.
        """
        self.storage: PersonaStorageHandler = storage_handler or PersonaStorageHandler()
        self.ui: SoloLevelingConsoleUI = user_interface or SoloLevelingConsoleUI()

        self.questions: List[Dict[str, Any]] = ONBOARDING_QUESTIONS
        self.responses: List[Dict[str, Any]] = []

    def run_questionnaire(self) -> None:
        """Executes sequential collection pipelines mapping answers alongside specified impact ranges."""
        self.responses.clear()
        for question in self.questions:
            self.ui.display_question_card(question)
            answer: str = self.ui.read_valid_answer()
            impact: int = self.ui.read_valid_impact_rating()

            self.responses.append(
                {
                    "question_id": question["id"],
                    "category": question["category"],
                    "question": question["question"],
                    "answer": answer,
                    "impact": impact,
                }
            )
            self.ui.render_progress_bar(question["id"], len(self.questions))

    def save_current_profile(self) -> Dict[str, int]:
        """Processes telemetry calculations and issues export commands to downstream file layers.

        Returns:
            Dict[str, int]: Priority count configuration statistics tracking profile weights.
        """
        stats: Dict[str, int] = {
            "high_count": sum(1 for r in self.responses if r["impact"] == 3),
            "medium_count": sum(1 for r in self.responses if r["impact"] == 2),
            "low_count": sum(1 for r in self.responses if r["impact"] == 1),
        }
        self.storage.write_persona_profile(self.responses, stats)
        return stats

    def execute_workflow(self) -> bool:
        """Launches state-machine processes managing onboarding setup workflows.

        Returns:
            bool: True if initialization executed smoothly or completed successfully, False otherwise.
        """
        try:
            if self.ui.display_welcome_screen():
                self.run_questionnaire()
                stats = self.save_current_profile()
                self.ui.display_completion_screen(
                    high_priority_count=stats["high_count"],
                    medium_priority_count=stats["medium_count"],
                    low_priority_count=stats["low_count"],
                    target_file_path=self.storage.persona_file,
                )
                return True
            else:
                self.storage.touch_setup_flag_only()
                self.ui.display_skip_notification()
                return False

        except KeyboardInterrupt:
            print("\n\n⚠️  Profile creation interrupted.")
            print("   Run SL again to complete setup.\n")
            return False
        except Exception as e:
            print(f"\n❌ Error during setup: {e}")
            print("   Please report this issue.\n")
            return False


# =====================================================================
# 4. COMPONENT ENTRY POINTS (Interface Layer Helpers)
# =====================================================================


def check_and_run_onboarding() -> bool:
    """Verifies baseline directory status launching workflows conditionally.

    Returns:
        bool: True if workflow runs cleanly or tracks pre-existing runs, False if skipped.
    """
    engine = PersonaOnboardingEngine()
    if engine.storage.is_first_time():
        return engine.execute_workflow()
    return False


def force_run_setup() -> bool:
    """Bypasses checks to re-run configuration workflows upon receiving manual user requests.

    Returns:
        bool: True if reconfiguration finishes without errors, False if revoked.
    """
    engine = PersonaOnboardingEngine()
    if not engine.storage.is_first_time():
        if not engine.ui.prompt_profile_recreation():
            return False

    return engine.execute_workflow()

