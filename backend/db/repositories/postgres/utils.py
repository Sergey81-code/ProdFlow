import re


def escape_tsquery(word: str) -> str:
    return re.sub(r"[^a-zA-Zа-яА-Я0-9_]", "", word)
