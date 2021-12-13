def try_parse_int(s, val=None):
  if s is None:
    return val

  try:
    return int(s)
  except ValueError:
    return val