import queue
import os
from threading import Lock, RLock

_max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH"))

_was_started_mutex = Lock()
_was_started = False

def on_successful_login():
  with _was_started_mutex:
    global _was_started
    _was_started = True

def is_logged_in():
  with _was_started_mutex:
    return _was_started

all_messages_mutex = RLock()
all_messages = []

def get_message_by_id(id):
  with all_messages_mutex:
    return next((m for m in all_messages if m.id == id), None)

_admin_user_ids = []
_admin_user_ids_lock = RLock()

def insert_admin(user_id):
  with _admin_user_ids_lock:
    _admin_user_ids.append(user_id)

def is_admin(user_id):
  with _admin_user_ids_lock:
    return user_id in _admin_user_ids

confirmation_code_queue = queue.Queue()

def get_message_content(msg):
  content = getattr(msg, "message", None)
  if (content is None or len(content) == 0) and is_voice_message(msg):
    content = "Sprachnachricht"
  if (content is None or len(content) == 0) and is_photo(msg):
    content = "Bild"

  return truncate_message(content)  

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
