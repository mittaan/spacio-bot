#!user/bin/env python3

# Imports

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
import os
from dotenv import load_dotenv
import json
from pathlib import Path
import logging.config
import logging.handlers
import atexit


# Global constants and config method

load_dotenv()

TEMPLATE_URL = "https://api.thecatapi.com/v1/images/search"

TEMPLATE_QUERY_URL = "?size={size}&mime_types={mime_types}&limit={limit}"

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

BOT_USERNAME = "@spaciocat_bot"

BOT_COMMANDS = [('/start', 'Starts a conversation with the bot.'),
                ('/help', 'Gives information on how to use the bot.'),
                ('/spacio', 'Get a random cat picture.'),
                ('/end', 'Ends the conversation with the bot.')]


# Logging

logger = logging.getLogger(__name__)

def setup_logging():
    config_file = Path("logging_config", "config.json")
    with open(config_file) as config_setup:
        config = json.load(config_setup)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


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
    message = update.message if update.message is not None else update.edited_message
    logger.info(f"User {message.from_user.id} in {message.chat.type}: {message.text}")
    keyboard = [[InlineKeyboardButton("Get started", callback_data="/help")]]

    await update.message.reply_text("Welcome! Get free cats here.\n/help for more info",
                                    reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message is not None else update.edited_message
    logger.info(f"User {message.from_user.id} in {message.chat.type}: {message.text}")
    commands_explained = [f"{command} {description}" for command, description in zip(commands, command_descriptions)]
    await update.message.reply_text(f"{"\n".join(commands_explained)}")

async def spacio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message is not None else update.edited_message
    logger.info(f"User {message.from_user.id} in {message.chat.type}: {message.text}")
    image_url = get_image_url()
    await update.message.reply_photo(image_url)


# Responses

def handle_response(text: str) -> str:
    if text in commands:
        return f"Executing command {text}"
    elif text == BOT_USERNAME:
        return "Hello! Need a cat?\nTry /spacio"
    return "Not a valid command,\nplease seek /help"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message is not None else update.edited_message
    chat_type: str = message.chat.type
    text: str = message.text
    command = [word for word in text.split() if word in valid_commands or BOT_USERNAME in word]

    if command != []:
        logger.info(f"User {message.from_user.id} in {chat_type}: {command}")
    else:
        return

    keyboard = []

    if "group" in chat_type:
        if BOT_USERNAME in text.split():
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            if new_text != "":
                response: str = handle_response(new_text)
            else:
                response: str = handle_response(BOT_USERNAME)
                keyboard.append([InlineKeyboardButton("Free kitty", callback_data="/spacio")])
                
        else:
            return
    else:
        if BOT_USERNAME in text.split():
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            if new_text != "":
                response: str = handle_response(new_text)
            else:
                response: str = handle_response(BOT_USERNAME)
                keyboard.append([InlineKeyboardButton("Free kitty", callback_data="/spacio")])
                
        else:
            response: str = handle_response(text)

    logger.info(f"Bot: {response}")

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard != [] else None

    await update.message.reply_text(response, reply_markup=reply_markup)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback = update.callback_query
    callback_data = update.callback_query.data

    match callback_data:
        case "/help":
            await help_command(callback, context)
        case "/spacio":
            await spacio_command(callback, context)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error_message = update.message if update.message is not None else update.edited_message
    logger.error(f"Update {error_message} from {update.message.from_user.id} caused error {context.error}")



if __name__ == "__main__":
    setup_logging()
    logging.basicConfig(level="INFO")

    logger.info("Starting bot...")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = app.bot
    commands, command_descriptions = zip(*BOT_COMMANDS)
    commands_with_bot_name = [command + BOT_USERNAME for command in commands]
    valid_commands = list(commands) + commands_with_bot_name
    valid_commands.append(BOT_USERNAME)

    headers = { 'x-api-key' : API_KEY }
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("spacio", spacio_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    logger.info("Polling...")
    app.run_polling(poll_interval=1)