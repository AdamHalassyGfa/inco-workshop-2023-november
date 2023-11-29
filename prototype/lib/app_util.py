import re


def str_to_int(text):
    return int(text.strip()) if re.match("\\s*[\\d]+\\s*", text or "") else None

