import html
import os
import time

from .api.deepLApi import DeepLAPI
from .api.huggingFaceApi import HuggingFaceAPI
from .api.imgbbApi import ImgbbAPI
from .api.instaApi import InstaAPI
from .api.htmlToImgApi import HtmlToImgApi

from .logger import logger

CURRENT_FOLDER = os.path.dirname(__file__)

class PromptValidator():
    def __init__(self):
        self._hugging_face_api = HuggingFaceAPI()

    def is_promptable(self, comment:str):
        # 1. clean spaces
        comment = comment.strip()  
        # 2. min characters and max characters
        if len(comment) <= 10 or len(comment) >= 200:
            return False   
        # 3. has not more than 70% of alpha numeric (got emote)
        alpha_nb = 0
        for c in comment.replace(" ", ""):
            if c.isalpha():
                alpha_nb = alpha_nb + 1
        if ((alpha_nb * 100) / len(comment.replace(" ", ""))) <= 70:
            return False
        # 3. no # or @ or http, wwww
        if any(char in comment for char in ["#", "@", "www", "http"]):
            return False 
        # 4. NFSW # Temporary disabled to test
        # if self._hugging_face_api.is_nsfw(comment):
        #     return False
        return True

class BotService():
    def __init__(self):
        self._insta_api = InstaAPI()
        self._hugging_face_api = HuggingFaceAPI()
        self._imgbb_api = ImgbbAPI()
        self._deepL_api = DeepLAPI()
        self._html_to_img_api = HtmlToImgApi()
        self._prompt_validator = PromptValidator()

    def get_last_media_id(self):
        data = self._insta_api.get_medias()
        media_id = None
        if len(data) == 0:
            logger.warning("No media found.")
        else:
            media_id = data[0]["id"]
            logger.info("Last media id '%s'", media_id)
        return media_id

    def select_prompt(self, media_id : str):
        best_comment = None
        if media_id:
            comments = self._insta_api.get_comments_from_media(media_id)
            if len(comments) > 0:
                promptables = []
                for comment in comments:
                    comment['text_translated'] = self._deepL_api.translate(comment["text"])
                    if self._prompt_validator.is_promptable(comment['text_translated']):
                        promptables.append(comment)
                best_comment = max(promptables, key=lambda comment: comment['like_count'] , default=None)
                if best_comment:
                    best_comment['text'] = best_comment['text_translated']
        if not best_comment:
            # generate prompt with tchat gpt ?
            logger.info("No comment has been selected. Generating internal prompt.")
            best_comment = {"text": "An Dog with a funny hat that look at us.",
                            "username" : "me"}

        return best_comment["text"], best_comment['username']

    def generate_image_from_prompt(self, best_prompt: str, output_path:str):
        self._hugging_face_api.generate_image(best_prompt, output_path)
        data = self._imgbb_api.upload_image(output_path)
        time.sleep(5) # time to be sure imge is fully uploaded
        return data['url']

    def publish_medias(self, img_urls: list[str], caption: str):
        container_ids = []
        for img_url in img_urls:
            payload = {
                "image_url": img_url,
                "is_carousel_item": True
            }
            container_ids.append(self._insta_api.create_container(payload))
            time.sleep(3)
        payload = {
            "children": ",".join(container_ids),
            "caption" : caption,
            "media_type": "CAROUSEL"
        }
        carousel_id = self._insta_api.create_container(payload)
        time.sleep(3)
        self._insta_api.publish_container(carousel_id)

    def generate_user_card(self, prompt:str, user_name: str, img_url: str) -> str:
        # Load templates
        html_template_path = os.path.join(CURRENT_FOLDER, "html","card.html")
        css_template_path = os.path.join(CURRENT_FOLDER, "html","style.css")  
        prompt = html.escape(prompt)
        username = html.escape(user_name)
        with open(html_template_path, encoding="utf8") as f :
            html_content = f.read()
        html_content = html_content.replace("{{USERNAME}}", username)
        html_content = html_content.replace("{{PROMPT}}", prompt)
        html_content = html_content.replace("{{PROFILE_IMAGE_URL}}", img_url)
        with open(css_template_path, encoding="utf8") as f :
            css_content = f.read()
        payload = { 'html': html_content, 'css': css_content }
        url = self._html_to_img_api.convert_html_to_image(payload)
        return url  