import html
import json
import re
import os
import time
import openai

from .api.deepLApi import DeepLAPI
from .api.huggingFaceApi import HuggingFaceAPI
from .api.imgbbApi import ImgbbAPI
from .api.instaApi import InstaAPI
from .api.htmlToImgApi import HtmlToImgApi
from .logger import logger, DAYS

CURRENT_FOLDER = os.path.dirname(__file__)

class PromptValidator():
    """ Class to validate and filter prompts/comments."""
    def __init__(self):
        self._hugging_face_api = HuggingFaceAPI()
        self._deepl_api = DeepLAPI()

    def clean_prompt(self, text: str):
        """
        Clean prompt text by removing unwanted parts.
        
        :param text (str): Original prompt text.
        :returns (str): Cleaned prompt text.
        """
        text = text.lower().replace("prompt:", "")
        return re.sub(r'[@#]\w+|prompt:', '', text).strip()

    def is_promptable(self, comment: str) -> bool:
        """
        Check if a comment is a valid prompt.
                
        :param comment (str): The comment to evaluate.
        :returns (bool): True if the comment is a valid prompt, otherwise False
        """
        if "prompt" not in comment.lower():
            return False
        if any(char in comment for char in ["www", "http"]):
            return False
        comment = self.clean_prompt(comment)
        # 2. min characters and max characters
        if len(comment) <= 10 or len(comment) >= 230:
            return False
        # 3. has not more than 70% of alpha numeric (got emote)
        alpha_nb = 0
        for c in comment.replace(" ", ""):
            if c.isalpha():
                alpha_nb = alpha_nb + 1
        if ((alpha_nb * 100) / len(comment.replace(" ", ""))) <= 70:
            return False
        return True

    def ia_filtering(self, prompts):
        """
        Filter prompts using LLM Open IA API.
        
        :param prompts: List of prompts to filter.
        :returns: Filtered list of prompts.
        """
        # filter with open ia
        prompts_analyzed = self.analyse_prompts(prompts)
        filtered_comments = []
        for i, p in enumerate(prompts_analyzed):
            if p["eligible"]:
                filtered_comments.append(prompts[i])
        return filtered_comments

    def is_nsfw(self, comment: str) -> bool:
        """
        Analyze if a comment is NSWF using HuggingFace API.

        :param comment (str): Comment to analyze.
        :returns (bool): True if the comment is NSFW, otherwise False.
        """
        return self._hugging_face_api.is_nsfw(comment)

    def analyse_prompts(self, prompts):
        """
        Analyze prompts using OpenAI API to classify them as eligible or not.
        :param prompts (str): List of prompts to analyze.
        :returns (list[dict]): List of analysis results.
        """
        # Fill user part
        user_message = "Classify the following texts:\n\n"
        for i, p in enumerate(prompts, start=1):
            user_message += f"{i}. \"{p['text']}\"\n"
        # Return JSON in this exact format:
        user_message += f"""
            Rules:
            - Return ONLY valid JSON (no markdown, no extra text)
            - The JSON must have exactly {len(prompts)} items in results
            - There must be one result per input line, with the same index (1..{len(prompts)})
            Return this JSON schema:
            {{
                "results": [
                    {{ "index": 1, "eligible": True, "reason": "short reason" }},
                ]
            }}
        """
        system_message = """
                        You are a strict classifier.
                        ELIGIBLE: Describes a drawable scene with a subject and at least one visual detail. May contain a few emojis.
                        NOT_ELIGIBLE: Reactions, compliments, emoji-only or emoji-dominant comments, engagement bait, vague or meta comments.
                        Respond ONLY with valid JSON. No extra text.
                    """
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # rapide et peu cher pour ce job
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0
        )
        return json.loads(response.choices[0].message.content)["results"]

    def filter_safe_comments(self, comments):
        """
        Translate and exclude NSFW comments.
        
        :param comments: comments to filter.
        :returns: List of safe comments.
        """
        safe_comments = []
        for c in comments:
            c["text_translated"] = self._deepl_api.translate(c["text"])
            if not self.is_nsfw(c["text_translated"]):
                c['text'] = c["text_translated"]
                safe_comments.append(c)

        return safe_comments

class BotService():
    """ Main bot service to coordinate API calls and business logic. """
    def __init__(self):
        self._insta_api = InstaAPI()
        self._hugging_face_api = HuggingFaceAPI()
        self._imgbb_api = ImgbbAPI()
        self._deepl_api = DeepLAPI()
        self._html_to_img_api = HtmlToImgApi()
        self._prompt_validator = PromptValidator()

    def get_last_media_id(self):
        """
        Get the last media id from Instagram page.
        
        :returns (str): The last media id.
        """
        data = self._insta_api.get_medias()
        media_id = None
        if len(data) == 0:
            logger.warning("No media found.")
        else:
            media_id = data[0]["id"]
            logger.info("Last media id '%s'", media_id)
        return media_id

    def select_prompt(self, media_id : str):
        """
        Select the best prompt from comments.
        
        :param media_id (str): Id of the media/post to get comments from.
        :returns (tuple): The best prompt and username.
        """
        best_comment = None
        if media_id:
            comments = self._insta_api.get_comments_from_media(media_id)
            if len(comments) > 0:
                promptValidator = PromptValidator()
                sorted_comments = sorted(comments, key=lambda c: -c["like_count"])[:10]
                simple_filtered_comments = [ {**c, "text": promptValidator.clean_prompt(c["text"])}
                                            for c in sorted_comments
                                            if promptValidator.is_promptable(c["text"])]
                ia_filtered_comments = promptValidator.ia_filtering(simple_filtered_comments)
                safe_comments = promptValidator.filter_safe_comments(ia_filtered_comments)
                if len(safe_comments) > 0:
                    best_comment = safe_comments[0]
        if not best_comment:
            # generate prompt with tchat gpt ?
            logger.info("No comment has been selected. Generating internal prompt.")
            best_comment = {"text": "An Dog with a funny hat that look at us.",
                            "username" : "me"}
        return best_comment["text"], best_comment['username']

    def generate_image_from_prompt(self, best_prompt: str, output_path:str):
        """
        Generate an image from prompt and upload it temporarily to imgbb.
        
        :param best_prompt (str): Prompt used to generate the image.
        :param output_path (str): Path to save the generated image.
        :returns (str): URL of the imgbb uploaded image.
        """
        self._hugging_face_api.generate_image(best_prompt, output_path)
        data = self._imgbb_api.upload_image(output_path)
        time.sleep(5) # time to be sure imge is fully uploaded
        return data['url']

    def publish_medias(self, img_urls: list[str], caption: str):
        """
        Publish medias on Instagram as a carousel.
        
        :param img_urls (list[str]): List of image URLs to publish.
        :param caption (str): Caption for the carousel.
        """
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
        """
        Generate a user card image from prompt, username and image URL.

        :param prompt (str): Prompt text.
        :param user_name (str): Username of prompt author.
        :param img_url (str): URL of the generated image.
        :returns: (str): URL of the generated user card image.
        """
        html_template_path = os.path.join(CURRENT_FOLDER, "html","card.html")
        css_template_path = os.path.join(CURRENT_FOLDER, "html","style.css")
        prompt = html.escape(prompt)
        username = html.escape(user_name)
        with open(html_template_path, encoding="utf8") as f :
            html_content = f.read()
        html_content = html_content.replace("{{USERNAME}}", username)
        html_content = html_content.replace("{{PROMPT}}", prompt)
        html_content = html_content.replace("{{PROFILE_IMAGE_URL}}", img_url)
        html_content = html_content.replace("{{DAYS}}", DAYS)
        with open(css_template_path, encoding="utf8") as f :
            css_content = f.read()
        payload = { 'html': html_content, 'css': css_content }
        url = self._html_to_img_api.convert_html_to_image(payload)
        return url
