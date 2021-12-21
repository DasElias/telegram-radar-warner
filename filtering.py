import shared
import csv
import utils 

_filter_words = []

def init_filtering():
  global _filter_words
  _filter_words = _read_csv("filter_always.csv")

def _read_csv(filename):
  list = []
  with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
      list.append(row[0])
  return list    

def should_filter(message, content, repliedToMessage):
  return _was_sent_by_admin(message) or \
          _has_no_content(message) or \
          _has_no_content(repliedToMessage) or \
          _contains_forbidden_string(content) or \
          (shared.has_message_replies(message) and not shared.is_reply_to_msg(message)) or \
          shared.was_message_answered_by_admin(message)

def _was_sent_by_admin(msg):
  if msg is None:
    return False
  return shared.was_message_sent_by_admin(msg)

def _has_no_content(msg):
  if msg is None:
    return False

  content = shared.get_message_content(msg) 
  return content is None or len(content) <= 1  

def _contains_forbidden_string(content):
  if content is None:
    return False

  for searchFor in _filter_words:
    if utils.contains_case_insensitive(content, searchFor):
      return True

  return False

