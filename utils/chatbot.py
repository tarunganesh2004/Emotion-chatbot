from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
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
