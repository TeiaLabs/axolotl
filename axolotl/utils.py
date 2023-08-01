import json

from rich import print


def pjson(obj):
    """Prettify JSON."""
    return json.dumps(obj, indent=4, sort_keys=True)


def ppjson(obj):
    """Pretty print JSON."""
    print(pjson(obj))
