import os
import deepl
from ..logger import logger

class DeepLAPI():  
    def __init__(self):
        self._api_key = os.getenv("DEEPL_API_KEY")
        self._client = deepl.DeepLClient(self._api_key)

    def translate(self, text_to_translate: str, target_lang:str="EN-US"):
        logger.info("Translate text '%s' to '%s' with DeepLAPI.", text_to_translate, target_lang)
        result = self._client.translate_text(text_to_translate, target_lang=target_lang)
        logger.info("Translation succeeded : '%s'", result.text)
        return result.text