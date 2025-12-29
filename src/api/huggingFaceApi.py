import os
from huggingface_hub import InferenceClient
from ..logger import logger 

# https://huggingface.co/docs/huggingface_hub/v0.13.2/en/quick-start
# 1. GENERATE TOKEN
# 2. pip install Pillow, huggingface_hub
# liens vers methode du client 
# https://huggingface.co/docs/huggingface_hub/v1.1.4/en/package_reference/inference_client#huggingface_hub.InferenceClient
# modele accessible avec ce client https://huggingface.co/inference/models

# TEMPORARY LOW QUALITY => TO DO : PUT BACK 1080 WHEN PROD
WIDTH = 1024 
HEIGHT = 1024

class HuggingFaceAPI():
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
                        
        logger.info("Generating image from api.")
        image = self._client.text_to_image(
            prompt,
            model=model,
            width=WIDTH,
            height=HEIGHT
        )

        image.save(output_path)
        logger.info("Image generated successfully in '%s', size: %sx%s.",
                    output_path, image.size[0], image.size[1])

    def is_nsfw(self, comment: str, max_score=0.6):
        result = self._client.text_classification(comment, 
                                                  model="eliasalbouzidi/distilbert-nsfw-text-classifier")
        logger.debug("Is '%s' NSFW ? %s : %s, %s : %s", comment, result[0]['label'], result[0]['score'], result[1]['label'], result[1]['score'])      
        return result[0]['label'].lower() == "nsfw" and result[0]['score'] > max_score    