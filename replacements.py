import csv
from utils import replace_case_insensitive

_replacements = []

def init_replacements():
  with open("replacements.csv", encoding="utf-8") as csvfile:
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

  prefixes = [" ", "/", "-", ".", ":", ","]
  suffixes = [" ", "/", "-", ".", ":", ","]

  for p in prefixes:
    for s in suffixes:
      str = _replace_message_impl(str, p, s)

  return str.strip()       

def _replace_message_impl(str, prefix, suffix):
  for r in _replacements:
    repl_from = prefix + r["from"].strip() + suffix
    repl_to = prefix + r["to"].strip() + suffix
    str = replace_case_insensitive(str, repl_from, repl_to)

  return str  


 