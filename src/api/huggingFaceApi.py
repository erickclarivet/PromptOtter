import os
from huggingface_hub import InferenceClient
from ..logger import logger as Logger

#https://huggingface.co/docs/huggingface_hub/v0.13.2/en/quick-start
#1. GENERATE TOKEN
#2. pip install Pillow, huggingface_hub
#liens vers methode du client
#modele accessible avec ce client https://huggingface.co/inference/models

#TEMPORARY LOW QUALITY => TO DO : PUT BACK 1024 WHEN PROD
WIDTH=1024
HEIGHT=1024

class HuggingFaceAPI():
    """ Class to interact wit Hugging Face API (Image generation/Check NSFW comment). """
    def __init__(self):
        self._api_key = os.getenv("HF_API_KEY")
        self._client = InferenceClient(
            provider="hf-inference", # quota atteint :(
            api_key= self._api_key,
        )

    def generate_image(self, prompt: str, output_path : str = 'result.jpeg',
                       model="black-forest-labs/FLUX.1-dev"):
                        # model="stabilityai/stable-diffusion-xl-base-1.0"):
                        # model="ByteDance/SDXL-Lightning"):
                        # model="black-forest-labs/FLUX.1-dev"):
        """
        Generate and image from a text using Hugging Face API.
        :param prompt (str): The text prompt to generate the image from.
        :param output_path (str): The output path to save the generated image.
        :param model (str): The model to use for image generation.
        """
        Logger.info("Generating image from api.")
        image = self._client.text_to_image(
            prompt,
            model=model,
            width=WIDTH,
            height=HEIGHT
        )

        image.save(output_path)
        Logger.info("Image generated successfully in '%s', size: %sx%s.",
                    output_path, image.size[0], image.size[1])

    def is_nsfw(self, comment: str, max_score=0.6):
        """
        Check if comment is NSFW using Hugging Face API.
        
        :param comment (str): Text used to check NSFW.
        :param max_score (float): Ratio to consider a text as NSFW.
        :returns (bool): True if comment is NSFW, False otherwise.
        """
        result = self._client.text_classification(comment,
                                            model="eliasalbouzidi/distilbert-nsfw-text-classifier")
        Logger.debug("Is '%s' NSFW ? %s : %s, %s : %s",
                     comment, result[0]['label'],
                     result[0]['score'], result[1]['label'], result[1]['score'])      
        return result[0]['label'].lower() == "nsfw" and result[0]['score'] > max_score
