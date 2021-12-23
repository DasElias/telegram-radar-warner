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

def replace_case_insensitive(text, old, new):
  idx = 0
  while idx < len(text):
    index_l = text.lower().find(old.lower(), idx)
    if index_l == -1:
      return text
    text = text[:index_l] + new + text[index_l + len(old):]
    idx = index_l + len(new) 
  return text

def contains_case_insensitive(text, searchFor):
  return text.lower().find(searchFor.lower()) != -1

def equals_case_insensitive(a, b):
  return a.lower() == b.lower()  

def to_human_readable_list(seq):
  # Ref: https://stackoverflow.com/a/53981846/
  seq = [str(s) for s in seq]
  if len(seq) < 3:
      return ' und '.join(seq)
  return ', '.join(seq[:-1]) + ', und ' + seq[-1]    

def filter_list(list, should_sort_out):
  filtered = []
  for e in list:
    if not should_sort_out(e):
      filtered.append(e)
  return filtered

def insert_sorted_list(list, new_elem, get_key = lambda x:x):
  for index, value in enumerate(list):
    if get_key(value) < get_key(new_elem):
      list.insert(index, new_elem)      
      return
  list.append(new_elem)  