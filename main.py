import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from telethon import TelegramClient
from flask import Flask
import threading
from webserver import web_server
from telegram import telegram_server
import replacements
import filtering

# Init replacements and filtering
replacements.init_replacements()
filtering.init_filtering()

# Enable connection
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
client = TelegramClient('radar_warner', api_id, api_hash)

app = Flask(__name__)
web_server(app)

# run server
if __name__ == "__main__":
  # start flask in a background thread so Telegram client can run in main thread
  def run_flask():
    app.run(host="0.0.0.0", port=5000)

  t1 = threading.Thread(target=run_flask, daemon=True)
  t1.start()

  client.loop.run_until_complete(telegram_server(client))
  client.run_until_disconnected()
