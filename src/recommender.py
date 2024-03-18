import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import os
import json
import pdb

with open("hf_key.json", "r") as file:
    hf_key = json.load(file)
os.environ["HF_TOKEN"] = hf_key["key"]


class Recommender:
    """Class to generate clothes recommendations based on the weather data.
    It uses the Hugging Face API to generate the recommendations.
    The class has a method to fill in a template with the weather data and a method to generate the recommendations."""
    def __init__(self):
        #get the token from hf_key.json file and set it as an environment variable
        self.model_id = "gg-hf/gemma-2b-it"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, torch_dtype = torch.bfloat16)
        self.template = self._get_template()

    def _get_template(self):
        # get template from file
        with open("config/template_recommendation.txt", "r") as file:
            template = file.read()
        return template
    
    def fill_in_template(self, time, timezone, currently, hourly):
        # fill in the template with the data
        return self.template.format(time = time, timezone = timezone, currently = currently, hourly = hourly)

    def generate_clothes_recommendation(self, input_text):
        """Method to generate the clothes recommendations based on the input text. 
        It uses the Hugging Face API to generate the recommendations.
        
        Args:
            input_text (str): The input text with the weather data.
        
        Returns:
            str: The clothes recommendations."""
        chat = [{ "role": "user", "content": input_text},]
        prompt = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
        outputs = self.model.generate(input_ids=inputs.to(self.model.device), max_new_tokens=200)
        outputs = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        start_index = outputs.find("model") + len("model\n")
        model_response = outputs[start_index:]
        return model_response


if __name__ == "__main__":
    generator = Recommender()
    input_text = "It's March 18th, I'm in Buenos Aires and the current weather is as following: 24°C, no rain probability for today. Recommend me clothes for today"
    reco = generator.generate_clothes_recommendation(input_text)
    print(reco)
