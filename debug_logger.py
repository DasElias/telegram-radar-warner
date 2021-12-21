from threading import Lock, RLock

_logs = []
_logs_mutex = Lock()

def log(*msg):
  with _logs_mutex:
    str = ""
    for m in msg:
      str += m + " "
    _logs.insert(0, str) 

def get_logs():
  with _logs_mutex:
    return list(_logs)