import os
from dotenv import load_dotenv
import threading, queue
from telethon import TelegramClient, events, sync
from telethon.tl.types import ChannelParticipantsAdmins
import hypercorn.asyncio
from quart import Quart, request, json

# Load environment variables
load_dotenv()

# Global variables
wasStarted = False
adminUserIds = []
allMessages = []
lock = threading.RLock()
q = queue.Queue()
defaultElemsReturned=5

# Telegram Server
async def get_code():
  code = q.get()
  return code;

def should_filter(message):
  return message.from_id.user_id in adminUserIds

# Enable connection
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
channel_username=os.getenv("CHANNEL")
client = TelegramClient('RadarWarner', api_id, api_hash)
client.start(phone_number, code_callback=get_code)
wasStarted = True

# Get chat entity
chat = client.get_entity(channel_username)

# Listen for new messages
@client.on(events.NewMessage(incoming=True, chats=chat))
async def handler(event):
  print("new message received")
  with lock:
    message = event.message
    if not should_filter(message):
      allMessages.insert(0, message)

# Get admins
for part in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
  adminUserIds.append(part.id)    

# Get recent messages
for message in client.get_messages(chat, limit=11):
  with lock:
    if not should_filter(message):
      allMessages.append(message)
    



# Web Server
api = Quart(__name__)

def try_parse_int(s, val=None):
  if s is None:
    return val

  try:
    return int(s)
  except ValueError:
    return val

def getMessageById(id):
  elem = next((m for m in allMessages if m.id == id), None)
  return getattr(elem, "message", None)

def mapMessage(msg):
  replyMessage = None;

  if msg.reply_to is not None:
    replyMessage = getMessageById(msg.reply_to.reply_to_msg_id)

  return {
    "message": msg.message,
    "id": msg.id,
    "date": msg.date,
    "replyMessage": replyMessage
  }

def get_all_messages(elems):
  with lock:
    return list(map(mapMessage, allMessages[:elems]))

def get_messages_human_readable(elems):
  resultString = ""
  for m in get_all_messages(elems):
    time = m["date"].strftime("%H:%M")
    resultString += time
    resultString += " "

    if m["replyMessage"] is not None:
      resultString += "Antwort auf \""
      resultString += m["replyMessage"]
      resultString += "\"\t"

    resultString += m["message"]
    resultString += "<br>"
    resultString += "\r\n"
  return resultString;  

@api.route('/messages/json', methods=['GET'])
def route_get_messages_json():
  if not wasStarted:
    return json.dumps({
      "message": "Please login first."
    })

  elems = try_parse_int(request.args.get("elems")) or defaultElemsReturned
  return json.dumps(get_all_messages(elems))
    
@api.route('/messages/text', methods=['GET'])
def route_get_messages_text():
  if not wasStarted:
    return "Bitte bestätige zuerst deinen Anmeldecode."

  elems = try_parse_int(request.args.get("elems")) or defaultElemsReturned
  return get_messages_human_readable(elems)

@api.route('/login', methods=['GET'])
def route_login():
  if wasStarted:
    return "Server is already running"

  try:
    key = request.args.get("key")
    q.put_nowait(key)
    return "Key placed"
  except queue.Full:
    return "Queue is already full."  



async def main():
  await hypercorn.asyncio.serve(api, hypercorn.Config())


if __name__ == '__main__':
  client.loop.run_until_complete(main())

