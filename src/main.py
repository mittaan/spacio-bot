#!user/bin/env python3

from PIL import Image
import requests
import yaml
from pathlib import Path

TEMPLATE_URL = "https://api.thecatapi.com/v1/images/search"

TEMPLATE_QUERY_URL = "?size={size}&mime_types={mime_types}&limit={limit}"

def set_config():
    path = Path("../config/config.yml")
    with open(path, "r") as config_file:
        config = yaml.safe_load(config_file)

    creadentials = config["credentials"]
    api_key = creadentials["api_key"]
    return { 'x-api-key' : api_key }

def set_query_url(size, mime_types, limit):
    temp_url_1 = TEMPLATE_QUERY_URL.replace("{size}", size)
    temp_url_2 = temp_url_1.replace("{mime_types}", mime_types)
    temp_url_3 = temp_url_2.replace("{limit}", str(limit))
    return temp_url_3

def get_search(headers, size="med", mime_types="jpg", limit=1):
    query_url = set_query_url(size, mime_types, limit)
    URL = TEMPLATE_URL + query_url
    r = requests.get(URL, headers=headers)
    data = r.json()
    return data

def get_image(url):
    image = Image.open(requests.get(url, stream=True).raw)
    image.show()

def main():
    headers = set_config()

    data = get_search(headers)

    image_url = data[0]["url"]
    get_image(image_url)

if __name__ == "__main__":
    print("Starting")
    main()
    print("Operation completed")