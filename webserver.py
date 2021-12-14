from Aeros import WebServer
from Aeros.misc import jsonify
from quart import request
import os
import queue
import helpers
import pytz
from pytz import timezone
import shared
from shared import all_messages, confirmation_code_queue

tz = timezone(os.getenv("TIMEZONE"))
default_elems_returned = int(os.getenv("DEFAULT_ELEMS_RETURNED"))

def getMessageById(id):
  elem = next((m for m in all_messages if m.id == id), None)
  return getattr(elem, "message", None)

def mapMessage(msg):
  date = msg.date.replace(tzinfo=pytz.utc).astimezone(tz)

  # Build reply message
  reply_message = None
  if msg.reply_to is not None:
    reply_message = getMessageById(msg.reply_to.reply_to_msg_id)
  
  # Build parsed message
  parsed_message = date.strftime("%H:%M") + "\t "

  if reply_message is not None:
    parsed_message += "Antwort auf\"" + reply_message + "\"\t "

  parsed_message += msg.message

  return {
    "originalMessage": msg.message,
    "id": msg.id,
    "date": date,
    "replyMessage": reply_message,
    "parsedMessage": parsed_message
  }  

def get_all_messages(elems):
  return list(map(mapMessage, all_messages[:elems]))

def get_messages_human_readable(elems):
  result_string = ""
  for m in get_all_messages(elems):
    result_string += m["parsedMessage"]
    result_string += "<br>"
    result_string += "\r\n"
  return result_string





def web_server(api):
  @api.route('/messages/json', methods=['GET'])
  async def route_get_messages_json():
    if not shared.was_started:
      return jsonify({
        "message": "Please login first."
      })

    elems = helpers.try_parse_int(request.args.get("elems")) or default_elems_returned
    return jsonify(get_all_messages(elems))
      
  @api.route('/messages/text', methods=['GET'])
  async def route_get_messages_text():
    if not shared.was_started:
      return "Bitte bestätige zuerst deinen Anmeldecode."

    elems = helpers.try_parse_int(request.args.get("elems")) or default_elems_returned
    return get_messages_human_readable(elems)    

  @api.route('/login', methods=['GET'])
  async def route_login():
    if shared.was_started:
      return "Server is already running"

    try:
      key = request.args.get("key")
      confirmation_code_queue.put_nowait(key)
      return "Key placed"
    except queue.Full:
      return "Queue is already full."  
