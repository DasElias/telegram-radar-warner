def try_parse_int(s, val=None):
  if s is None:
    return val

  try:
    return int(s)
  except ValueError:
    return val

def try_parse_bool(s, val=False):
  if s is None:
    return val

  return s.lower() in ['true', '1', 't', 'y', 'yes']