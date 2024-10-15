#!user/bin/env python3

import requests
import yaml
from pathlib import Path

TEMPLATE_URL = "https://graph.instagram.com/"

TAG_ID_URL = TEMPLATE_URL + "ig_hashtag_search?user_id=<USER_ID>&q=cats"

TOP_MEDIA_URL = TEMPLATE_URL + "<TAG_ID>/top_media?user_id=<USER_ID>"

def get_tag_id(user_id):
    URL = TAG_ID_URL.replace("<USER_ID>", str(user_id))
    r = requests.get(URL)
    data = r.json()
    return data["id"]

def get_top_media_id(tag_id, user_id):
    URL = TOP_MEDIA_URL.replace("<USER_ID>", str(user_id)).replace("<TAG_ID>", str(tag_id))
    r = requests.get(URL)
    data = r.json()
    return data

def main():
    path = Path("../config/config.yml")
    with open(path, "r") as config_file:
        config = yaml.safe_load(config_file)

    creadentials = config["credentials"]
    user_id = creadentials["user_id"]
    tag_id = get_tag_id(user_id)

    data = get_top_media_id(tag_id, user_id)
    print(data)


if __name__ == "__main__":
    main()