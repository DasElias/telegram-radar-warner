import queue
from threading import Lock, RLock

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


confirmation_code_queue = queue.Queue()
