"""Frame matching and blending for smooth transitions"""

import numpy as np
import cv2
from typing import Tuple, Optional, List
from dataclasses import dataclass
from .frame_extractor import FrameData


@dataclass
class FrameMatch:
    """Frame matching result"""
    similarity_score: float  # 0.0 to 1.0
    reference_frame: FrameData
    current_frame: FrameData
    keypoint_matches: int
    feature_distance: float


class FrameMatcher:
    """Matches and blends frames for seamless scene transitions"""

    def __init__(self, threshold: float = 0.80, blend_frames: int = 3):
        """
        Initialize frame matcher.

        Args:
            threshold: Minimum similarity score for frames
            blend_frames: Number of frames to blend for smooth transitions
        """
        self.threshold = threshold
        self.blend_frames = blend_frames
        # Initialize feature detector (SIFT or AKAZE)
        self.detector = cv2.SIFT_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

    def match_frames(self, ref_frame: FrameData, curr_frame: FrameData) -> FrameMatch:
        """
        Match two frames and calculate similarity.

        Args:
            ref_frame: Reference frame from previous segment
            curr_frame: Current frame from new segment

        Returns:
            FrameMatch with similarity metrics
        """
        # Detect keypoints and descriptors
        kp1, des1 = self.detector.detectAndCompute(ref_frame.image_array, None)
        kp2, des2 = self.detector.detectAndCompute(curr_frame.image_array, None)

        if des1 is None or des2 is None:
            # Fallback to structural similarity if no keypoints found
            structural_sim = self._calculate_ssim(ref_frame.image_array, curr_frame.image_array)
            return FrameMatch(
                similarity_score=structural_sim,
                reference_frame=ref_frame,
                current_frame=curr_frame,
                keypoint_matches=0,
                feature_distance=0.0
            )

        # Match descriptors using KNN
        matches = self.matcher.knnMatch(des1, des2, k=2)

        # Apply Lowe's ratio test to filter good matches
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

        # Calculate similarity score
        similarity = self._calculate_match_score(len(good_matches), len(kp1), len(kp2))

        # Calculate average feature distance
        avg_distance = np.mean([m.distance for m in good_matches]) if good_matches else 0.0

        return FrameMatch(
            similarity_score=similarity,
            reference_frame=ref_frame,
            current_frame=curr_frame,
            keypoint_matches=len(good_matches),
            feature_distance=avg_distance
        )

    def blend_frames(self, frame1: np.ndarray, frame2: np.ndarray,
                    num_frames: int = 3, algorithm: str = "linear") -> List[np.ndarray]:
        """
        Blend between two frames for smooth transition.

        Args:
            frame1: First frame (ending frame of previous segment)
            frame2: Second frame (starting frame of next segment)
            num_frames: Number of intermediate frames to generate
            algorithm: Blending algorithm (linear, cubic, gaussian)

        Returns:
            List of blended frames
        """
        if frame1.shape != frame2.shape:
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))

        blended_frames = []

        for i in range(1, num_frames + 1):
            alpha = i / (num_frames + 1)

            if algorithm == "linear":
                blended = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
            elif algorithm == "cubic":
                # Cubic easing for smoother transition
                alpha = self._cubic_easing(alpha)
                blended = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
            elif algorithm == "gaussian":
                # Gaussian blur for smoother falloff
                blended = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
                blended = cv2.GaussianBlur(blended, (5, 5), 0)
            else:
                blended = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)

            blended_frames.append(blended)

        return blended_frames

    def create_smooth_transition(self, end_frame: FrameData, start_frame: FrameData,
                                transition_type: str = "fade") -> List[np.ndarray]:
        """
        Create smooth transition between two frames.

        Args:
            end_frame: Ending frame of previous segment
            start_frame: Starting frame of next segment
            transition_type: Type of transition (fade, wipe, dissolve)

        Returns:
            List of transition frames
        """
        if transition_type == "fade":
            return self.blend_frames(end_frame.image_array, start_frame.image_array,
                                   num_frames=self.blend_frames, algorithm="linear")
        elif transition_type == "wipe":
            return self._create_wipe_transition(end_frame.image_array, start_frame.image_array)
        elif transition_type == "dissolve":
            return self.blend_frames(end_frame.image_array, start_frame.image_array,
                                   num_frames=self.blend_frames, algorithm="gaussian")
        else:
            return self.blend_frames(end_frame.image_array, start_frame.image_array,
                                   num_frames=self.blend_frames)

    def detect_scene_boundaries(self, frames: List[FrameData],
                               threshold: float = 0.3) -> List[int]:
        """
        Detect scene boundaries based on frame differences.

        Args:
            frames: List of consecutive frames
            threshold: Threshold for detecting scene changes

        Returns:
            List of frame indices where scene changes occur
        """
        boundaries = []

        for i in range(1, len(frames)):
            hist1 = cv2.calcHist([frames[i-1].image_array], [0, 1, 2], None, [8, 8, 8],
                                [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([frames[i].image_array], [0, 1, 2], None, [8, 8, 8],
                                [0, 256, 0, 256, 0, 256])

            diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)

            if diff > threshold:
                boundaries.append(i)

        return boundaries

    @staticmethod
    def _calculate_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate Structural Similarity Index (SSIM) between two images.
        """
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Calculate SSIM
        score = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
        return float(np.mean(score))

    @staticmethod
    def _calculate_match_score(num_matches: int, num_kp1: int, num_kp2: int) -> float:
        """
        Calculate match score based on keypoint matches.
        """
        if num_kp1 == 0 or num_kp2 == 0:
            return 0.0

        match_ratio = num_matches / max(num_kp1, num_kp2)
        return float(min(match_ratio, 1.0))

    @staticmethod
    def _cubic_easing(t: float) -> float:
        """
        Cubic easing function for smooth transitions.
        """
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def _create_wipe_transition(frame1: np.ndarray, frame2: np.ndarray,
                               num_frames: int = 5, direction: str = "left") -> List[np.ndarray]:
        """
        Create a wipe transition effect between frames.
        """
        if frame1.shape != frame2.shape:
            frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))

        frames = []
        height, width = frame1.shape[:2]

        for i in range(1, num_frames + 1):
            alpha = i / (num_frames + 1)
            wipe_pos = int(width * alpha)

            if direction == "left":
                wipe_frame = np.copy(frame1)
                wipe_frame[:, :wipe_pos] = frame2[:, :wipe_pos]
            elif direction == "right":
                wipe_frame = np.copy(frame1)
                wipe_frame[:, wipe_pos:] = frame2[:, wipe_pos:]
            else:
                wipe_frame = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)

            frames.append(wipe_frame)

        return frames
