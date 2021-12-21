from Aeros import WebServer
from Aeros.misc import jsonify
from quart import request
import os
import queue
from filtering import should_filter
import helpers
import pytz
from pytz import timezone
from datetime import datetime, timedelta
import replacements
import shared
from shared import confirmation_code_queue, get_message_content
import utils
from filtering import should_filter
import debug_logger

tz = timezone(os.getenv("TIMEZONE"))
default_elems_returned = int(os.getenv("DEFAULT_ELEMS_RETURNED"))




def mapMessage(msg):
  date = msg.date.replace(tzinfo=pytz.utc).astimezone(tz)
  truncated_orig_message = get_message_content(msg)
  replaced_message = replacements.replace_message(truncated_orig_message)

  # Build reply message
  reply_message = None
  if msg.reply_to is not None:
    reply_message = get_message_content(shared.get_message_by_id(msg.reply_to.reply_to_msg_id))
    reply_message = replacements.replace_message(reply_message)
  
  # Build parsed message
  time_string = date.strftime("%H:%M")
  parsed_message = ""

  if reply_message is not None:
    parsed_message += "Antwort auf \"" + reply_message + "\"\t "

  parsed_message += replaced_message

  return {
    "id": msg.id,
    "dateTime": date,
    "type": shared.get_message_type(msg),
    "userId": msg.from_id.user_id,
    "originalMessage": msg.message,
    "timeString": time_string,
    "replyToMessage": reply_message,
    "parsedMessage": time_string + "\t " + parsed_message,
    "parsedMessageWithoutTime": parsed_message
  }  

def get_additional_messages_object(only_media_messages):
  length = len(only_media_messages)
  if length > 0:
    time_list = list(map(lambda msg: msg["timeString"], only_media_messages))

    msg = get_additional_messages_prefix(only_media_messages) + " um " + utils.to_human_readable_list(time_list) + " empfangen"
    return {
      "originalMessage": None,
      "id": None,
      "date": None,
      "timeString": None,
      "replyMessage": None,
      "parsedMessage": msg,
      "parsedMessageWithoutTime": msg,
      "type": "summary",
      "userId": None
    }
  else:
    return None  

def get_additional_messages_prefix(only_media_messages):
  length = len(only_media_messages)
  if length == 1:
    type = only_media_messages[0]["type"]
    if type == "voice":
      return "Weitere Sprachnachricht"
    if type == "photo":
      return "Weiteres Bild"
    else:
      return "Weitere Nachricht"
  if length > 0:
    if all(msg["type"] == "voice" for msg in only_media_messages):
      return "Weitere Sprachnachrichten"
    if all(msg["type"] == "photo" for msg in only_media_messages):
      return "Weitere Bilder"
    return "Weitere Sprachnachrichten und Bilder"
  return None

def append_or_concat_message(list, new_msg):
  if len(list) > 0:
    last_msg = list[-1]
    if last_msg["userId"] == new_msg["userId"]:
      last_msg["id"] = [new_msg["id"], last_msg["id"]]
      last_msg["type"] = [new_msg["type"], last_msg["type"]]
      last_msg["parsedMessage"] = new_msg["parsedMessage"] + " - " + last_msg["parsedMessageWithoutTime"]
      last_msg["parsedMessageWithoutTime"] = new_msg["parsedMessageWithoutTime"] + " - " + last_msg["parsedMessageWithoutTime"]
      last_msg["originalMessage"] = new_msg["originalMessage"] + " - " + last_msg["originalMessage"]
      # userId don't needs to be updated
      # time and date neither
      return

  list.append(new_msg)  

def get_all_messages(elems):
  only_media_messages = []
  filtered_messsages = []

  with shared.get_all_messages_mutex():
    i = 0
    min_date = tz.localize(datetime.now()) - timedelta(hours = 1.5)
    is_next_date_after_min = True
    while (len(filtered_messsages) < elems or is_next_date_after_min) and shared.get_amount_of_messages() > i:
      msg = shared.get_nth_message(i)
      reply_to_msg = shared.get_reply_to_msg(msg)

      mapped = mapMessage(msg)
      if not should_filter(msg, mapped["parsedMessage"], reply_to_msg):
        if shared.is_multimedia_message_without_content(msg):
          only_media_messages.append(mapped)
        else:
          append_or_concat_message(filtered_messsages, mapped)
      else:
        print("should filter: ", msg.message)    

      i = i + 1
      is_next_date_after_min = shared.get_amount_of_messages() > i and shared.get_nth_message(i).date > min_date  

    additional_msg = get_additional_messages_object(only_media_messages)
    if additional_msg is not None:
      filtered_messsages.append(additional_msg)

    return filtered_messsages

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
    if not shared.is_logged_in():
      return jsonify({
        "message": "Please login first."
      })

    elems = helpers.try_parse_int(request.args.get("elems")) or default_elems_returned
    return jsonify(get_all_messages(elems))
      
  @api.route('/messages/text', methods=['GET'])
  async def route_get_messages_text():
    if not shared.is_logged_in():
      return "Bitte bestätige zuerst deinen Anmeldecode."

    elems = helpers.try_parse_int(request.args.get("elems")) or default_elems_returned
    return get_messages_human_readable(elems)    

  @api.route('/login', methods=['GET'])
  async def route_login():
    if shared.is_logged_in():
      return "Server is already running"

    try:
      key = request.args.get("key")
      confirmation_code_queue.put_nowait(key)
      return "Key placed"
    except queue.Full:
      return "Queue is already full."  

  @api.route('/messages/all', methods=['GET'])
  async def route_get_messages_all():
    if not shared.is_logged_in():
      return "Bitte bestätige zuerst deinen Anmeldecode."

    str = ""
    with shared.get_all_messages_mutex():
      for m in shared.get_all_messages():
        str += m.stringify()
        str += "<br>"  

    return str

  @api.route('/logs', methods=['GET'])
  async def route_get_logs():
    return jsonify(debug_logger.get_logs())