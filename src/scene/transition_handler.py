"""Transition handling between scenes"""

from typing import List, Optional, Dict
from dataclasses import dataclass
import numpy as np


@dataclass
class Transition:
    """Represents a transition between two scenes"""
    from_scene_id: str
    to_scene_id: str
    transition_type: str  # fade, cut, wipe, dissolve
    duration_frames: int
    blend_strength: float = 0.5


class TransitionHandler:
    """Handles smooth transitions between scenes"""

    def __init__(self):
        self.transitions: Dict[str, Transition] = {}
        self.default_duration = 3  # frames

    def create_transition(self, from_scene_id: str, to_scene_id: str,
                         transition_type: str = "fade",
                         duration_frames: int = 3) -> Transition:
        """
        Create a transition between two scenes.

        Args:
            from_scene_id: ID of source scene
            to_scene_id: ID of target scene
            transition_type: Type of transition
            duration_frames: Duration in frames

        Returns:
            Transition object
        """
        transition_id = f"{from_scene_id}_to_{to_scene_id}"
        transition = Transition(
            from_scene_id=from_scene_id,
            to_scene_id=to_scene_id,
            transition_type=transition_type,
            duration_frames=duration_frames
        )
        self.transitions[transition_id] = transition
        return transition

    def get_transition(self, from_scene_id: str, to_scene_id: str) -> Optional[Transition]:
        """
        Get transition between two scenes.

        Args:
            from_scene_id: ID of source scene
            to_scene_id: ID of target scene

        Returns:
            Transition object or None
        """
        transition_id = f"{from_scene_id}_to_{to_scene_id}"
        return self.transitions.get(transition_id)

    def update_transition(self, from_scene_id: str, to_scene_id: str,
                         **kwargs) -> Optional[Transition]:
        """
        Update transition properties.

        Args:
            from_scene_id: ID of source scene
            to_scene_id: ID of target scene
            **kwargs: Properties to update

        Returns:
            Updated Transition or None
        """
        transition = self.get_transition(from_scene_id, to_scene_id)
        if not transition:
            return None

        for key, value in kwargs.items():
            if hasattr(transition, key):
                setattr(transition, key, value)

        return transition

    def calculate_transition_duration(self, transition: Transition) -> float:
        """
        Calculate transition duration in seconds (assuming 24 FPS).

        Args:
            transition: Transition object

        Returns:
            Duration in seconds
        """
        return transition.duration_frames / 24.0

    def generate_transition_prompt_modifier(self, transition: Transition) -> str:
        """
        Generate prompt modifier for smooth transitions.

        Args:
            transition: Transition object

        Returns:
            Prompt modifier string
        """
        modifiers = {
            "fade": "seamless fade transition, matching lighting and composition",
            "cut": "sharp cut to next scene",
            "wipe": "wipe transition effect",
            "dissolve": "dissolve transition with smooth color blending",
            "smooth": "continuous motion, seamless scene flow"
        }
        return modifiers.get(transition.transition_type, modifiers["smooth"])
