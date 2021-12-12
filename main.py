import os
from dotenv import load_dotenv
import threading, queue
from telethon import TelegramClient, events, sync
import asyncio
from flask import Flask, json, request
from waitress import serve

load_dotenv();

api = Flask(__name__)

wasStarted = False
allMessages = []
lock = threading.RLock()
q = queue.Queue()
defaultElemsReturned=5

def telegramServer():
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)

  async def get_code():
    code = q.get()
    return code;

  api_id = os.getenv("API_ID")
  api_hash = os.getenv("API_HASH")
  phone_number = os.getenv("PHONE_NUMBER")
  channel_username=os.getenv("CHANNEL")
  client = TelegramClient('RadarWarner', api_id, api_hash)
  client.start(phone_number, code_callback=get_code)

  global wasStarted
  wasStarted = True

  chat = client.get_entity(channel_username)


  @client.on(events.NewMessage(incoming=True, chats=chat))
  async def handler(event):
    print(event.stringify())
    with lock:
      allMessages.insert(0, event.message)
      print("new message received")

  for message in client.get_messages(chat, limit=11):
    with lock:
      allMessages.append(message)
      print(message.stringify())


  with client:
    client.run_until_disconnected()

def webServer():

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
      resultString += "\r\n"
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
      return "Server is already running";

    try:
      key = request.args.get("key")
      q.put_nowait(key)
      return "Key placed"
    except queue.Full:
      return "Queue is already full."  

  port = os.getenv("PORT")
  serve(api, port=port)


if __name__=='__main__':
  t1 = threading.Thread(target=telegramServer, name="Telegram")
  t1.start()
  webServer()
