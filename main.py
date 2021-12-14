import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from telethon import TelegramClient
from Aeros import WebServer, AdvancedThread
from webserver import web_server
from telegram import telegram_server


# Enable connection
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
client = TelegramClient('radar_warner', api_id, api_hash)

app = WebServer(__name__, host="0.0.0.0", port=5000)
web_server(app)

# run server
if __name__ == "__main__":
  t1 = AdvancedThread(target=app.run_server)
  t1.start()

  client.loop.run_until_complete(telegram_server(client))
  client.run_until_disconnected()
