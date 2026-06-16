"""Character visual consistency engine"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConsistencyScore:
    """Character consistency scoring result"""
    character_id: str
    score: float  # 0.0 to 1.0
    appearance_score: float
    pose_score: float
    lighting_score: float
    timestamp: str
    details: Dict


class ConsistencyEngine:
    """Analyzes and maintains character visual consistency across scenes"""

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.consistency_history: List[ConsistencyScore] = []

    def analyze_consistency(self, character_id: str, reference_embedding: np.ndarray,
                           current_embedding: np.ndarray, pose_data: Dict = None) -> ConsistencyScore:
        """
        Analyze consistency between reference and current character state.

        Args:
            character_id: ID of the character
            reference_embedding: Original character embedding
            current_embedding: Current frame character embedding
            pose_data: Optional pose information

        Returns:
            ConsistencyScore with detailed metrics
        """
        # Calculate appearance consistency (cosine similarity)
        appearance_score = self._cosine_similarity(reference_embedding, current_embedding)

        # Calculate pose consistency if available
        pose_score = self._analyze_pose_consistency(pose_data) if pose_data else 1.0

        # Estimate lighting consistency (simplified)
        lighting_score = self._estimate_lighting_consistency(reference_embedding, current_embedding)

        # Combined score (weighted average)
        overall_score = (
            0.5 * appearance_score +
            0.3 * pose_score +
            0.2 * lighting_score
        )

        score = ConsistencyScore(
            character_id=character_id,
            score=overall_score,
            appearance_score=appearance_score,
            pose_score=pose_score,
            lighting_score=lighting_score,
            timestamp=datetime.utcnow().isoformat(),
            details={
                "threshold_met": overall_score >= self.threshold,
                "warning": "Low consistency detected" if overall_score < self.threshold else None
            }
        )

        self.consistency_history.append(score)
        return score

    def get_consistency_trend(self, character_id: str, limit: int = 10) -> List[float]:
        """Get recent consistency scores for a character"""
        scores = [s.score for s in self.consistency_history
                 if s.character_id == character_id][-limit:]
        return scores

    def is_consistent(self, score: ConsistencyScore) -> bool:
        """Check if character is consistent enough for output"""
        return score.score >= self.threshold

    def get_consistency_report(self, character_id: str) -> Dict:
        """Generate consistency report for a character"""
        scores = [s for s in self.consistency_history if s.character_id == character_id]
        if not scores:
            return {"message": "No consistency data available"}

        all_scores = [s.score for s in scores]
        return {
            "character_id": character_id,
            "total_frames_analyzed": len(scores),
            "average_consistency": np.mean(all_scores),
            "min_consistency": np.min(all_scores),
            "max_consistency": np.max(all_scores),
            "consistency_std_dev": np.std(all_scores),
            "threshold": self.threshold,
            "meets_threshold_percentage": (sum(1 for s in all_scores if s >= self.threshold) / len(all_scores) * 100)
        }

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0

        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-10)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-10)
        return float(np.dot(vec1_norm, vec2_norm))

    @staticmethod
    def _analyze_pose_consistency(pose_data: Dict) -> float:
        """Analyze pose consistency (simplified)"""
        if not pose_data or "keypoints" not in pose_data:
            return 1.0

        # Calculate stability of keypoints
        keypoints = pose_data.get("keypoints", [])
        if len(keypoints) < 2:
            return 1.0

        # Simplified: check if pose variance is reasonable
        pose_variance = np.var([kp.get("confidence", 1.0) for kp in keypoints])
        return float(1.0 - min(pose_variance * 0.5, 0.2))

    @staticmethod
    def _estimate_lighting_consistency(ref_embedding: np.ndarray, curr_embedding: np.ndarray) -> float:
        """Estimate lighting consistency between frames"""
        if len(ref_embedding) == 0 or len(curr_embedding) == 0:
            return 1.0

        # Use brightness variation as proxy for lighting
        ref_brightness = np.mean(ref_embedding[:10]) if len(ref_embedding) >= 10 else 0.5
        curr_brightness = np.mean(curr_embedding[:10]) if len(curr_embedding) >= 10 else 0.5

        brightness_diff = abs(ref_brightness - curr_brightness)
        return float(max(0.0, 1.0 - brightness_diff))
