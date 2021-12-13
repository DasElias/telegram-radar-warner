import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from telethon import TelegramClient
from webserver import web_server, api
from telegram import telegram_server



# Enable connection
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
client = TelegramClient('radar_warner', api_id, api_hash)

# run server
client.loop.create_task(telegram_server(client))
client.loop.run_until_complete(web_server())
