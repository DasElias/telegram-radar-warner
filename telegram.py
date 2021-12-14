import os
from telethon import TelegramClient, events, sync
from telethon.tl.types import ChannelParticipantsAdmins

import shared
from shared import all_messages, confirmation_code_queue, was_started

phone_number = os.getenv("PHONE_NUMBER")
channel_username=os.getenv("CHANNEL")
default_elems_fetched = int(os.getenv("DEFAULT_ELEMS_FETCHED"))

admin_user_ids = []

async def get_confirmation_code():
  code = confirmation_code_queue.get()
  return code

def should_filter(message):
  return message.from_id.user_id in admin_user_ids
  

async def telegram_server(client):
  await client.start(phone_number, code_callback=get_confirmation_code)

  shared.was_started = True

  # Get chat entity
  chat = await client.get_entity(channel_username)

  # Listen for new messages
  @client.on(events.NewMessage(incoming=True, chats=chat))
  async def handler(event):
    message = event.message
    if not should_filter(message):
      all_messages.insert(0, message)
      print(message.stringify())

  async for part in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
    admin_user_ids.append(part.id)   

  async for message in client.iter_messages(chat, limit=default_elems_fetched):
    if not should_filter(message):
      all_messages.append(message)

