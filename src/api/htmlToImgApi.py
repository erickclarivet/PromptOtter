import os
import requests
from ..logger import logger

class HtmlToImgApi():
    """ HTML to Image API client. """
    def __init__(self):
        self._root_url = "https://hcti.io/v1"
        self._api_key = os.getenv("HCTI_API_KEY")
        self._user_id = os.getenv("HCTI_API_USER_ID")

    def convert_html_to_image(self, payload) -> str:
        """
        Convert HTML content to an image using the HCTI API.
        
        :param payload (dict): The payload containing HTML content and options.
        :returns (str): The URL of the generated image.
        """
        r = requests.post(url = f"{self._root_url}/image",
                          data = payload, auth=(self._user_id, self._api_key),
                          timeout=60)
        r.raise_for_status()
        url = r.json()['url']
        logger.info("Html has been converted to image with success: %s", url)
        return url
