import queue
import os
from threading import Lock, RLock
import utils
from telethon.tl.types import MessageEntityBotCommand
import replacements

_max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH"))
_default_elems_fetched = int(os.getenv("DEFAULT_ELEMS_FETCHED"))

_was_started_mutex = Lock()
_was_started = False

def on_successful_login():
  with _was_started_mutex:
    global _was_started
    _was_started = True

def is_logged_in():
  with _was_started_mutex:
    return _was_started

_all_messages_mutex = RLock()
_all_messages = []

def get_all_messages_mutex():
  return _all_messages_mutex

def get_all_messages():
  return _all_messages

def get_amount_of_messages():
  return len(_all_messages)

def get_nth_message(n):
  return _all_messages[n]    

def insert_message(message):
  msg_content = get_message_content(message)
  message.replaced_message_content = replacements.replace_message(msg_content)

  with _all_messages_mutex:
    utils.insert_sorted_list(_all_messages, message, lambda m: m.id)
    if len(_all_messages) > _default_elems_fetched:
      _all_messages.pop()

def get_replaced_message_content(message):
  if message is None:
    return ""
  else :
    return message.replaced_message_content

def get_message_by_id(id):
  with _all_messages_mutex:
    return next((m for m in _all_messages if m.id == id), None)

def remove_message_by_id(id):
  with _all_messages_mutex:
    global _all_messages
    _all_messages = utils.filter_list(_all_messages, lambda msg: msg.id == id)

def get_reply_to_msg(msg):
  if msg.reply_to is not None:
    return get_message_by_id(msg.reply_to.reply_to_msg_id)
  return None  

def get_replies(msg):
  replies = []
  for m in _all_messages:
    if m.reply_to is not None and m.reply_to.reply_to_msg_id == msg.id:
      replies.append(m)

  return replies    

def has_message_replies(msg):
  for m in _all_messages:
    if m.reply_to is not None and m.reply_to.reply_to_msg_id == msg.id:
      return True

    # there can't be replies before the message was sent  
    if m.id == msg.id:
      break
  return False

def is_reply_to_msg(msg):
  return msg.reply_to is not None

def contains_bot_command(msg):
  if msg.entities is None:
    return False
    
  return any(isinstance(e, MessageEntityBotCommand) for e in msg.entities)
          

def was_message_answered_by_admin(msg):
  for m in _all_messages:
    if m.reply_to is not None and m.reply_to.reply_to_msg_id == msg.id and was_message_sent_by_admin(m):
      return True

    # there can't be replies before the message was sent  
    if m.id == msg.id:
      break

  return False

_admin_user_ids = []
_admin_user_ids_lock = RLock()

def insert_admin(user_id):
  with _admin_user_ids_lock:
    _admin_user_ids.append(user_id)

def is_admin(user_id):
  with _admin_user_ids_lock:
    return user_id in _admin_user_ids

def was_message_sent_by_admin(msg):
  return is_admin(msg.from_id.user_id)    

confirmation_code_queue = queue.Queue()

def get_message_content(msg):
  type = get_message_type(msg)
  
  content = getattr(msg, "message", None)
  if type == "voice":
    return "Sprachnachricht"
  if type == "photo":
    return "Bild"
  return truncate_message(content)


def get_message_type(msg):
  content = getattr(msg, "message", None)
  if (content is None or len(content) == 0) and is_voice_message(msg):
    return "voice"
  if (content is None or len(content) == 0) and is_photo(msg):
    return "photo"     
  return "text"  

def is_multimedia_message_without_content(msg):  
  return getattr(msg, "message", None) != get_message_content(msg)

def is_voice_message(msg):
  media = getattr(msg, "media", None)
  document = getattr(media, "document", None)
  return document is not None

def is_photo(msg):
  media = getattr(msg, "media", None)
  document = getattr(media, "photo", None)
  return document is not None

def truncate_message(msg):
  if msg is None:
    return None

  # 3 characters are appended
  truncate_behind = _max_message_length + 3
  if(len(msg) > truncate_behind):
    msg = msg[:truncate_behind] + "..."  
    
  return msg
