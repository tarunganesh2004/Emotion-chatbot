from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import random
import logging

logger = logging.getLogger(__name__)


class Chatbot:
    def __init__(self):
        self.model_name = "microsoft/DialoGPT-medium"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.emotion_prompts = {
            "happy": "You are a cheerful chatbot. The user is happy. Respond with enthusiasm: ",
            "sad": "You are a supportive chatbot. The user is sad. Respond empathetically: ",
            "angry": "You are a calming chatbot. The user is angry. Respond soothingly: ",
            "neutral": "You are a friendly chatbot. Respond naturally: ",
            "disgust": "You are a reassuring chatbot. The user is disgusted. Respond with understanding: ",
            "fear": "You are a comforting chatbot. The user is fearful. Respond with reassurance: ",
            "surprise": "You are an engaging chatbot. The user is surprised. Respond with curiosity: ",
        }
        self.emotion_reducers = {
            "happy": [
                "That’s awesome to see! Keep spreading that positivity!",
                "Your happiness is infectious! Let’s keep the good vibes going!",
            ],
            "sad": [
                "Here’s a virtual hug for you! Things will get better soon.",
                "I’m here for you—maybe a funny movie can lift your spirits?",
            ],
            "angry": [
                "Take a deep breath—let’s find a way to calm things down together.",
                "I get it, things can be frustrating. How about a quick break to relax?",
            ],
            "neutral": [
                "Let’s make things more exciting—any fun ideas?",
                "How about we chat about something that makes you smile?",
            ],
            "disgust": [
                "I totally get why you’d feel that way—let’s talk about something more pleasant!",
                "That sounds unpleasant! How about we focus on something that makes you feel better?",
            ],
            "fear": [
                "You’re safe here with me—let’s take a moment to breathe and relax.",
                "I’m here to support you—maybe a calming story can help ease your mind?",
            ],
            "surprise": [
                "That’s quite a reaction! What caught you off guard—let’s explore it!",
                "Wow, that must’ve been unexpected! Want to share more about it?",
            ],
        }

    def generate_response(self, user_input, emotion="neutral"):
        try:
            prompt = (
                self.emotion_prompts.get(emotion, self.emotion_prompts["neutral"])
                + user_input
            )
            inputs = self.tokenizer.encode(
                prompt + self.tokenizer.eos_token, return_tensors="pt"
            )
            outputs = self.model.generate(
                inputs, max_length=100, pad_token_id=self.tokenizer.eos_token_id
            )
            response = self.tokenizer.decode(
                outputs[:, inputs.shape[-1] :][0], skip_special_tokens=True
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Chatbot response generation failed: {str(e)}")
            return "Sorry, I'm having trouble responding right now. Let's try again!"

    def generate_emotion_response(self, emotion="neutral"):
        try:
            why_message = f"Why are you {'' if emotion == 'neutral' else 'feeling '}{emotion} like that?"
            reducer = random.choice(
                self.emotion_reducers.get(emotion, self.emotion_reducers["neutral"])
            )
            return f"{why_message} {reducer}"
        except Exception as e:
            logger.error(f"Emotion response generation failed: {str(e)}")
            return "I noticed how you're feeling—let's chat about it!"
