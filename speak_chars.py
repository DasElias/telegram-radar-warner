def replace_to_speak_chars(str):
  if str is None:
    return str

  str = str.replace("?", " Fragezeichen - ")
  str = str.replace("!", " Rufezeichen - ")
  return str