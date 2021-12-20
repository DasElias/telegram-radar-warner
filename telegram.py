import os
from telethon import TelegramClient, events, sync
from telethon.tl.types import ChannelParticipantsAdmins

import shared
from shared import confirmation_code_queue, on_successful_login

phone_number = os.getenv("PHONE_NUMBER")
channel_username=os.getenv("CHANNEL")
default_elems_fetched = int(os.getenv("DEFAULT_ELEMS_FETCHED"))

async def get_confirmation_code():
  code = confirmation_code_queue.get()
  return code


async def telegram_server(client):
  await client.start(phone_number, code_callback=get_confirmation_code)
  on_successful_login()

  # Get chat entity
  chat = await client.get_entity(channel_username)

  # Listen for new messages
  @client.on(events.NewMessage(incoming=True, chats=chat))
  async def handler(event):
    message = event.message
    print("new message received", message.message)
    shared.insert_message_at_front(message)

  @client.on(events.MessageDeleted(chats=chat))
  async def deleted_handler(event):
    for msg_id in event.deleted_ids:
      shared.remove_message_by_id(msg_id)

  @client.on(events.MessageEdited(chats=chat))
  async def edited_handler(event):
    print("EVENT EDITED")
    print(event.stringify())   

  @client.on(events.ChatAction(chats=chat))
  async def edited_handler(event):
    print("EVENT ChatAction")
    print(event.stringify()) 

  async for part in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
    shared.insert_admin(part.id)   

  async for message in client.iter_messages(chat, limit=default_elems_fetched):
    shared.insert_message_at_back(message)

