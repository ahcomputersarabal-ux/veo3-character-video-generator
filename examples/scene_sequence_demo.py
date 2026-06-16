"""Example: Scene sequencing with frame matching"""

from src.config import get_settings
from src.scene.scene_manager import SceneManager
from src.scene.prompt_builder import PromptBuilder
from src.scene.transition_handler import TransitionHandler
from src.video.frame_matcher import FrameMatcher


def main():
    print("=" * 60)
    print("Veo 3 Scene Sequencing Demo")
    print("=" * 60)

    # Initialize managers
    scene_manager = SceneManager()
    prompt_builder = PromptBuilder()
    transition_handler = TransitionHandler()
    frame_matcher = FrameMatcher(threshold=0.80)

    # Create a sequence of scenes
    print("\n[Step 1] Creating scene sequence...")
    scene_prompts = [
        ("intro", "Introduction", "A cinematic wide shot of mountains at sunrise"),
        ("action", "Action", "A character performing an action in nature"),
        ("climax", "Climax", "An intense moment with dramatic lighting"),
        ("resolution", "Resolution", "A peaceful moment overlooking the landscape")
    ]

    scenes = []
    for scene_id, name, description in scene_prompts:
        scene = scene_manager.add_scene(
            scene_id=scene_id,
            name=name,
            description=description,
            prompt=description,
            duration=6
        )
        scenes.append(scene)
        print(f"✓ Scene created: {name} (ID: {scene_id})")

    # Display scene sequence
    print("\n[Step 2] Scene Sequence Order:")
    sequence = scene_manager.get_scene_sequence()
    for i, scene in enumerate(sequence, 1):
        print(f"  {i}. {scene.name} - {scene.description}")

    # Create transitions between scenes
    print("\n[Step 3] Creating transitions...")
    for i in range(len(scenes) - 1):
        from_scene = scenes[i]
        to_scene = scenes[i + 1]
        
        transition = transition_handler.create_transition(
            from_scene_id=from_scene.id,
            to_scene_id=to_scene.id,
            transition_type="smooth",
            duration_frames=3
        )
        
        modifier = transition_handler.generate_transition_prompt_modifier(transition)
        print(f"✓ Transition: {from_scene.name} → {to_scene.name}")
        print(f"  Type: {transition.transition_type}")
        print(f"  Duration: {transition_handler.calculate_transition_duration(transition):.2f}s")
        print(f"  Modifier: {modifier}")

    # Build frame-aware prompts
    print("\n[Step 4] Building frame-aware prompts...")
    for i, scene in enumerate(sequence):
        # Get transition info if applicable
        transition = None
        if i > 0:
            transition = transition_handler.get_transition(sequence[i-1].id, scene.id)
        
        if transition:
            prompt = prompt_builder.add_transition_hint(
                scene.prompt,
                transition_type=transition.transition_type
            )
        else:
            prompt = scene.prompt
        
        print(f"\n  Scene {i+1}: {scene.name}")
        print(f"  Prompt: {prompt[:100]}...")

    # Calculate total video duration
    print("\n[Step 5] Video Statistics:")
    total_duration = sum(s.duration for s in scenes)
    num_transitions = len(scenes) - 1
    transition_duration = sum(
        transition_handler.calculate_transition_duration(
            transition_handler.get_transition(scenes[j].id, scenes[j+1].id)
        )
        for j in range(len(scenes) - 1)
    )
    
    print(f"  Total scenes: {len(scenes)}")
    print(f"  Scenes duration: {total_duration}s")
    print(f"  Transitions: {num_transitions}")
    print(f"  Transitions duration: {transition_duration:.2f}s")
    print(f"  Total video duration: {total_duration + transition_duration:.2f}s")

    print("\n" + "=" * 60)
    print("Scene Sequencing Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
