#!user/bin/env python3

# Imports

from PIL import Image
import time
import requests
import telepot
from telepot.loop import MessageLoop
import yaml
from pathlib import Path


# Global constants and config method

TEMPLATE_URL = "https://api.thecatapi.com/v1/images/search"

TEMPLATE_QUERY_URL = "?size={size}&mime_types={mime_types}&limit={limit}"

def set_config():
    """
    Extracts the secrets stored in the config.yml file and returns it as a dictionary.

    To see how to structure the 'config.yml' file, please refer to the 'config.yml.example' file.
    """

    path = Path("../config/config.yml")
    with open(path, "r") as config_file:
        config = yaml.safe_load(config_file)

    credentials = config["credentials"]
    return credentials

CREDENTIALS = set_config()

API_KEY = CREDENTIALS["api_key"]
BOT_TOKEN = CREDENTIALS["bot_token"]



# Global variables

bot = telepot.Bot(BOT_TOKEN)

headers = { 'x-api-key' : API_KEY }


# Methods

def set_query_url(size, mime_types, limit):
    """
    Helper function to set the chosen parameters in the url query.
    """

    temp_url_1 = TEMPLATE_QUERY_URL.replace("{size}", size)
    temp_url_2 = temp_url_1.replace("{mime_types}", mime_types)
    temp_url_3 = temp_url_2.replace("{limit}", str(limit))
    return temp_url_3


def get_search(headers, size="med", mime_types="jpg", limit=1):
    """
    Retrieves the data at the specified API endpoint and returns it as a JSON object.
    """

    query_url = set_query_url(size, mime_types, limit)
    URL = TEMPLATE_URL + query_url
    r = requests.get(URL, headers=headers)
    data = r.json()
    return data


def handle(message):
    content_type, chat_type, chat_id = telepot.glance(message)
    print(content_type, chat_type, chat_id)

    data = get_search(headers)
    image_url = data[0]["url"]

    if content_type == "text":
        bot.sendPhoto(chat_id, image_url)


# def get_image(url):
#     image = Image.open(requests.get(url, stream=True).raw)
#     return image


def main():

    # get_image(image_url)
    MessageLoop(bot, handle).run_as_thread()
    print("Listening...")

    while 1:
        time.sleep(10)


if __name__ == "__main__":
    print("Starting")
    main()