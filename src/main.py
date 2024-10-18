#!user/bin/env python3

# Imports

from PIL import Image           # TODO: check if I can remove it
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yaml
from pathlib import Path
import asyncio


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

BOT_USERNAME = "@spaciocat_bot"

BOT_COMMANDS = [('/start', 'Starts a conversation with the bot.'),
                ('/help', 'Gives information on how to use the bot.'),
                ('/spacio', 'Get a random cat picture.')]



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

def get_image_url():
    data = get_search(headers)
    image_url: str = data[0]["url"]
    return image_url


# Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Get free cats here.\n/help for more info")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_explained = [f"{command} {description}" for command, description in zip(commands, command_descriptions)]
    await update.message.reply_text(f"{"\n".join(commands_explained)}")

async def spacio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image_url = get_image_url()
    await update.message.reply_photo(image_url)

# TODO: add end_command to close the bot


# Responses

def handle_response(text: str) -> str:
    if text in commands:
        return "test"
    return "Not a valid command"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {chat_type}: '{text}'")

    if chat_type == "group":
        if BOT_USERNAME in text.split():
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)   # TODO: correct the response to choose the correct command
        else:
            return
    else:
        response: str = handle_response(text)

    print(f"Bot: {response}")

    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")



if __name__ == "__main__":
    print("Starting bot...")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = app.bot
    commands, command_descriptions = zip(*BOT_COMMANDS)

    headers = { 'x-api-key' : API_KEY }
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("spacio", spacio_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=1)