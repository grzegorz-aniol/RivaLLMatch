import textwrap
from datetime import datetime


def wrap(text, width=120):
    return "\n".join(textwrap.wrap(text, width=width))


def now():
    return datetime.now().timestamp()
