"""Example: Character consistency demonstration"""

import os
from src.config import get_settings
from src.character.character_manager import CharacterManager
from src.character.consistency_engine import ConsistencyEngine
from src.scene.scene_manager import SceneManager
from src.scene.prompt_builder import PromptBuilder
from src.video.veo3_client import Veo3Client, VideoGenerationRequest
import numpy as np


def main():
    # Initialize managers
    character_manager = CharacterManager()
    consistency_engine = ConsistencyEngine(threshold=0.85)
    scene_manager = SceneManager()
    prompt_builder = PromptBuilder()

    settings = get_settings()
    veo3_client = Veo3Client(
        api_key=settings.google_api_key,
        model="veo3-fast"
    )

    print("=" * 60)
    print("Veo 3 Character Consistency Demo")
    print("=" * 60)

    # Step 1: Create a character
    print("\n[Step 1] Creating character...")
    character = character_manager.add_character(
        id="protagonist_01",
        name="Emma",
        description="A woman with long dark hair, fair complexion, wearing a blue dress, confident posture",
        reference_images=[]  # Would normally include paths to reference images
    )
    print(f"✓ Character created: {character.name} (ID: {character.id})")
    print(f"  Description: {character.description}")

    # Step 2: Create scenes
    print("\n[Step 2] Creating scenes...")
    scenes = []
    scene_descriptions = [
        ("scene_01", "Forest Walk", "Woman walking through a lush forest"),
        ("scene_02", "River Crossing", "Woman crossing a flowing river"),
        ("scene_03", "Mountain View", "Woman standing on a mountain overlooking valleys")
    ]

    for scene_id, scene_name, scene_desc in scene_descriptions:
        scene = scene_manager.add_scene(
            scene_id=scene_id,
            name=scene_name,
            description=scene_desc,
            prompt=scene_desc,
            character_id=character.id,
            duration=6
        )
        scenes.append(scene)
        print(f"✓ Scene created: {scene_name}")

    # Step 3: Build consistent prompts
    print("\n[Step 3] Building consistent prompts...")
    for scene in scenes:
        prompt = prompt_builder.build_prompt(
            scene=scene,
            character_description=character.description,
            template="cinematic"
        )
        print(f"  Scene: {scene.name}")
        print(f"  Prompt: {prompt[:80]}...")
        scene_manager.update_scene(scene.id, prompt=prompt)

    # Step 4: Generate videos with consistency checks
    print("\n[Step 4] Simulating video generation with consistency...")
    
    # Simulate character embeddings
    reference_embedding = np.random.rand(512)
    
    for i, scene in enumerate(scenes):
        print(f"\n  Generating: {scene.name}")
        
        # Simulate video generation
        request = VideoGenerationRequest(
            prompt=scene.prompt,
            duration=scene.duration,
            resolution="4K",
            model="veo3-fast",
            quality="high"
        )
        
        # Simulate current frame embedding
        current_embedding = reference_embedding + np.random.rand(512) * 0.1
        
        # Check consistency
        consistency = consistency_engine.analyze_consistency(
            character_id=character.id,
            reference_embedding=reference_embedding,
            current_embedding=current_embedding
        )
        
        print(f"  ✓ Consistency Score: {consistency.score:.2f}")
        print(f"    - Appearance: {consistency.appearance_score:.2f}")
        print(f"    - Pose: {consistency.pose_score:.2f}")
        print(f"    - Lighting: {consistency.lighting_score:.2f}")
        
        if consistency.is_consistent:
            print(f"  ✓ Character consistency maintained")
        else:
            print(f"  ⚠ Warning: Low consistency detected")
    
    # Step 5: Generate consistency report
    print("\n[Step 5] Consistency Report")
    report = consistency_engine.get_consistency_report(character.id)
    print(f"  Total scenes analyzed: {report['total_frames_analyzed']}")
    print(f"  Average consistency: {report['average_consistency']:.2f}")
    print(f"  Consistency threshold: {report['threshold']}")
    print(f"  Meets threshold: {report['meets_threshold_percentage']:.1f}%")

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
