"""Intelligent prompt building for consistent character videos"""

from typing import Optional, Dict, List
from .scene_manager import Scene


class PromptBuilder:
    """Builds and enriches prompts for character consistency"""

    def __init__(self):
        self.templates = {
            "standard": "{action} {character_desc} {setting}",
            "cinematic": "Cinematic scene: {action} with {character_desc} in {setting}. Professional lighting, sharp focus, high quality.",
            "detailed": "{character_desc} is {action} in {setting}. Detailed environment, realistic lighting, professional quality.",
            "action": "{character_desc} {action} in {setting}. Dynamic movement, cinematic composition."
        }

    def build_prompt(self, scene: Scene, character_description: str,
                    last_frame_description: Optional[str] = None,
                    template: str = "cinematic") -> str:
        """
        Build a consistent prompt for video generation.

        Args:
            scene: Scene object with prompt information
            character_description: Character appearance description
            last_frame_description: Description of last frame for continuity
            template: Template to use

        Returns:
            Enhanced prompt for video generation
        """
        template_str = self.templates.get(template, self.templates["cinematic"])

        # Extract components from scene prompt
        action, setting = self._parse_scene_prompt(scene.prompt)

        # Build character consistency string
        char_str = character_description
        if last_frame_description:
            char_str += f", continuing from: {last_frame_description}"

        # Build final prompt
        prompt = template_str.format(
            action=action,
            character_desc=char_str,
            setting=setting
        )

        # Add quality hints
        prompt = self._add_quality_hints(prompt)

        return prompt

    def build_batch_prompts(self, scenes: List[Scene], character_description: str,
                           last_frames: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Build prompts for multiple scenes with consistency.

        Args:
            scenes: List of scenes
            character_description: Character appearance
            last_frames: Mapping of scene IDs to last frame descriptions

        Returns:
            List of prompts for each scene
        """
        prompts = []
        for scene in scenes:
            last_frame_desc = last_frames.get(scene.id) if last_frames else None
            prompt = self.build_prompt(scene, character_description, last_frame_desc)
            prompts.append(prompt)
        return prompts

    def add_transition_hint(self, prompt: str, transition_type: str = "smooth") -> str:
        """
        Add transition hint to prompt for seamless joints.

        Args:
            prompt: Original prompt
            transition_type: Type of transition (smooth, cut, fade)

        Returns:
            Prompt with transition hint
        """
        hints = {
            "smooth": "seamless continuation, matching last frame composition",
            "cut": "sharp cut, new angle",
            "fade": "fade transition with matching lighting"
        }
        hint = hints.get(transition_type, hints["smooth"])
        return f"{prompt} ({hint})"

    @staticmethod
    def _parse_scene_prompt(prompt: str) -> tuple:
        """
        Parse scene prompt into action and setting components.

        Args:
            prompt: Scene prompt

        Returns:
            Tuple of (action, setting)
        """
        # Simple parsing logic - can be enhanced
        parts = prompt.split(" in ")
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return prompt, "unknown setting"

    @staticmethod
    def _add_quality_hints(prompt: str) -> str:
        """
        Add quality and style hints to prompt.

        Args:
            prompt: Original prompt

        Returns:
            Enhanced prompt with quality hints
        """
        quality_hints = " Ultra high quality, 4K resolution, professional cinematography, natural lighting, smooth motion."
        return prompt + quality_hints
