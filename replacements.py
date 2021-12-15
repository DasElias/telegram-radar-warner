import csv

_replacements = []

def init_replacements():
  with open("replacements.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
      _replacements.append({
        "from": row[0],
        "to": row[1]
      })

def replace_message(str):
  if str is None:
    return str

  str = " " + str + " "  

  prefixes = [" ", "/", "-"]
  suffixes = [" ", "/", "-"]

  for p in prefixes:
    for s in suffixes:
      str = _replace_message_impl(str, p, s)

  return str.strip()       

def _replace_message_impl(str, prefix, suffix):
  for r in _replacements:
    repl_from = prefix + r["from"] + suffix
    repl_to = prefix + r["to"] + suffix
    str = _replace_case_insensitive(str, repl_from, repl_to)

  return str  


def _replace_case_insensitive(text, old, new):
  idx = 0
  while idx < len(text):
    index_l = text.lower().find(old.lower(), idx)
    if index_l == -1:
      return text
    text = text[:index_l] + new + text[index_l + len(old):]
    idx = index_l + len(new) 
  return text  