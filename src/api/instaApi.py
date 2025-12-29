

import os
import requests
from ..logger import logger

class InstaAPI():   
    def __init__(self):
        self._root_graph_fb_url = "https://graph.facebook.com"
        self._insta_page_id = "17841478567581944"
        self._media_url = f"{self._root_graph_fb_url}/{self._insta_page_id}/media" 
        self._access_token = os.getenv("INSTA_ACCESS_TOKEN")
        self._headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-type": "application/json"
        }

    def get_medias(self):
        logger.info("Getting all medias from page.")
        r = requests.get(self._media_url, headers=self._headers, timeout=60)
        r.raise_for_status()
        data = r.json()["data"]
        logger.info("Medias have been retrieved successfully : %s.", data)
        return data

    def get_comments_from_media(self, media_id, fields="id,text,username,like_count,timestamp"):
        logger.info("Getting all comments from media id '%s'.", media_id)
        comments_from_media_url = f"{self._root_graph_fb_url}/{media_id}/comments?fields={fields}" 
        r = requests.get(comments_from_media_url, headers=self._headers, timeout=60)
        r.raise_for_status()
        data = r.json()["data"]
        logger.debug(data)
        logger.info("Comments have been retrieved successfully")
        return data            
    
    def create_container(self, payload):
        logger.info("Creating container.")
        r = requests.post(self._media_url, data=payload, headers=self._headers, timeout=60)
        r.raise_for_status()
        container_id = r.json()["id"]
        logger.info("Container has been created with success: id '%s'", container_id)
        return container_id
    
    def publish_container(self, container_id: str):
        media_publish_url = f"{self._media_url}_publish"
        payload = {
            "creation_id": container_id
        }
        logger.info("Publishing container/media.")
        r = requests.post(media_publish_url, data=payload, headers=self._headers, timeout=60)
        r.raise_for_status()
        logger.debug(r.json())
        logger.info("Container/media has been published with success.")
