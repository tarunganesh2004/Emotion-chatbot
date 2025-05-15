import cv2
from deepface import DeepFace
import logging

logger = logging.getLogger(__name__)


def detect_emotion(image):
    try:
        result = DeepFace.analyze(image, actions=["emotion"], enforce_detection=False)
        return result[0]["dominant_emotion"].lower()
    except Exception as e:
        logger.warning(f"Emotion detection failed: {str(e)}. Defaulting to neutral.")
        return "neutral"
