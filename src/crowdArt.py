from requests.exceptions import RequestException, HTTPError
from .botService import BotService
from .logger import logger, DAYS

def main():
    """
    Main function to run the CrowdArt bot service.
    """
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
                🏆 Most liked wins after {{DAYS}} days

                #aiart #promptchallenge #communityart

            """.replace("{{USERNAME}}", username).replace("{{DAYS}}", DAYS)
        bot_service.publish_medias([img_url, user_card_url], caption)
    except HTTPError as e:
        logger.critical("HTTP error occurred: %s", e)
    except RequestException as e:
        logger.critical("A request error occurred: %s", e)
    except Exception as e:
        logger.critical("An error occured: %s", e)

if __name__ == "__main__":
    main()
