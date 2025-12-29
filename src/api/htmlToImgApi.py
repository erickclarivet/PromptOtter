import os
import requests
from ..logger import logger
from ..logger import logger

class HtmlToImgApi():
    def __init__(self):
        self._root_url = "https://hcti.io/v1"
        self._api_key = os.getenv("HCTI_API_KEY")
        self._user_id = os.getenv("HCTI_API_USER_ID")
    
    def convert_html_to_image(self, payload) -> str:
        r = requests.post(url = f"{self._root_url}/image",
                          data = payload, auth=(self._user_id, self._api_key),
                          timeout=60)
        r.raise_for_status()
        url = r.json()['url']
        logger.info("Html has been converted to image with success: %s", url)
        return url
