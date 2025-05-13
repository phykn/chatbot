import json
import requests
from typing import List, Optional
from .misc import exists


def stream_post(
    url: str, 
    model: str, 
    messages: List[str], 
    options: Optional[dict] = None
):
    data = {
        "model": model,
        "messages": messages,
        "stream": True,
        "keep_alive": -1
    }

    if exists(options):
        data["options"] = options
    
    return requests.post(
        url = f"{url}/api/chat",
        json = data,
        stream = True
    )


def stream_parse(stream):
    for data in stream.iter_lines():
        try:
            data = json.loads(data.decode("utf-8"))
            content = data["message"]["content"]
            yield content

        except Exception as error_msg:
            yield error_msg
            break