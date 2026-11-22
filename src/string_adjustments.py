"""Report title and emoji formatting from the UCF Crimes monorepo."""

import json
import re
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=2)
def read_lookup(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def titlize(title: str) -> str:
    exceptions = read_lookup("title_exceptions.json")
    return " ".join(exceptions.get(token, token.title()) for token in title.split())


def get_emojis(title: str) -> str:
    suffix = ""
    for pattern, emojis in read_lookup("emojis.json").items():
        if re.search(pattern, title, re.IGNORECASE):
            for emoji in emojis:
                if emoji not in suffix:
                    suffix += emoji
    return suffix
