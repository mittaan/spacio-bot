#!user/bin/env python3

import requests

URL = "https://graph.instagram.com/v1/shortcode/<SHORTCODE>"

PARAMS = {'fields': ['id', 'media_product_type'], 'access_token': 1}

if __name__ == "__main__":
    pass