option_init = {
    "url": "http://localhost:8080",
    "model": "Qwen3:8B",
    "max_token": 1024,    
    "do_think": False
}


model_table = {
    "Qwen3:8B":{
        "name": "qwen3:8b",
        "is_vision": False,
        "is_think": True,
        "extensions": ["think"]
    },
    "Qwen3:30B":{
        "name": "qwen3:30b",
        "is_vision": False,
        "is_think": True,
        "extensions": ["think"]
    }
}