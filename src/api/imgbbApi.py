import os
import base64
import requests
from ..logger import logger

class ImgbbAPI():
    def __init__(self):
        self._api_key = os.getenv("IMGBB_API_KEY")
        self._root_url = "https://api.imgbb.com/1"
   
    def upload_image(self, image_path:str, expiration:str = "500"):
        logger.info("Encoding image in base64.")
        upload_url = f"{self._root_url}/upload"
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        payload = {"key": self._api_key,
                   "image": encoded_string,
                   "expiration": expiration}
        logger.info("Uploading image in imgbb.")
        r = requests.post(upload_url, data=payload, timeout=60)
        r.raise_for_status()
        data = r.json()["data"]
        logger.debug(data)
        logger.info("Image has been uploaded on imgbb successfully.")
        return data