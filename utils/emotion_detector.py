import cv2
from fer import FER
import logging

logger = logging.getLogger(__name__)


def detect_emotion(image):
    try:
        detector = FER(mtcnn=True)
        result = detector.detect_emotions(image)
        if result:
            emotions = result[0]["emotions"]
            dominant_emotion = max(emotions, key=emotions.get)
            return dominant_emotion.lower()
        return "neutral"
    except Exception as e:
        logger.warning(f"Emotion detection failed: {str(e)}. Defaulting to neutral.")
        return "neutral"
