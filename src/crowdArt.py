# import html
# import os
# import time
import json
import os
import requests
import openai
from src.api.huggingFaceApi import HuggingFaceAPI

from .botService import BotService
# from .api.deepLApi import DeepLAPI
# from .api.huggingFaceApi import HuggingFaceAPI
# from .api.imgbbApi import ImgbbAPI
# from .api.instaApi import InstaAPI
# from .api.htmlToImgApi import HtmlToImgApi

from .logger import logger

def main():
    try:
        bot_service = BotService()
        media_id = bot_service.get_last_media_id()
        best_prompt, username = bot_service.select_prompt(media_id)
        img_url = bot_service.generate_image_from_prompt(best_prompt, f"{username}.jpeg")
        user_card_url = bot_service.generate_user_card(best_prompt, username, img_url)
        caption = """
            
                This artwork was chosen by the community 👇

                🏆 Prompt by @{{USERNAME}} (see slide 2)

                Want Otto to paints yours ?

                ➕ Follow
                ✏️ Comment on the latest post (start with “Prompt:”)
                ❤️ Like to vote
                🏆 Most liked wins after 3 days

                #aiart #promptchallenge #communityart

            """.replace("{{USERNAME}}", username)
        bot_service.publish_medias([img_url, user_card_url], caption)
    except requests.exceptions.HTTPError as e:
        logger.critical("HTTP error occurred: %s", e)
    except requests.exceptions.RequestException as e:
        logger.critical("A request error occurred: %s", e)
    except Exception as e:
        logger.critical("An error occured: %s", e)

if __name__ == "__main__":
    # ret = HuggingFaceAPI().is_image_generation_prompt("Wow 🔥amazing 😍send us this pic")
    #logger.info(ret)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompts = [
        "Prompt: A realistic cat wearing a red hat, studio lighting",
        "Wow 🔥 amazing 😍 send us this pic",
        "Draw a cat with a pretty hat"
    ]

    # Construire le message utilisateur
    user_message = "Classify the following texts:\n\n"
    for i, p in enumerate(prompts, start=1):
        user_message += f"{i}. \"{p}\"\n"

    user_message += """
    Return JSON in this exact format:
    {
    "results": [
        { "index": 1, "eligible": true, "reason": "short reason" }
    ]
    }
    """

    response = client.chat.completions.create(
        model="gpt-4.1-nano",  # rapide et peu cher pour ce job
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict classifier.\n\n"
                    "ELIGIBLE means:\n"
                    "- Describes something visible that can be drawn\n"
                    "- Has a subject and at least one visual detail\n\n"
                    "NOT ELIGIBLE means:\n"
                    "- Reactions, compliments, emojis\n"
                    "- Engagement bait (like, follow, send pic)\n"
                    "- Vague or meta comments\n\n"
                    "Answer ONLY with valid JSON. No extra text."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0
    )

    # Récupérer et parser le JSON
    raw = response.choices[0].message.content
    data = json.loads(raw)

    print(json.dumps(data, indent=2))
    #main()
    
# TO DO :
# - TOKEN in env + REFRESH FB TOKEN => DONE perime en février v 
# - upload container : sleep not good, upload fail sometimes => next => HOW ?? v
# - better choose prompt from comment (validate method check NSFW, no copyright) v 
#   => good but to test, prob translate text to english first ? => NOT GOOD not translate emote 
#   => translate with deepL => good, but not from all languages ! v
# - refacto => Done
# - Add comments => TODO
# - paggination of comments => FAIRE CA
# - best model to generate image => CEST MORT POUR LE POC , a voir plus tard
# - graphical design + history + theme of instagram page => tourner autour des animaux et des chapeaux car c'est mignon !!
# - Tests ?
# - push to save
# - care same resolution both image !