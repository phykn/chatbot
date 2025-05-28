import json


def obj_to_str(obj):      
    return json.dumps(obj, ensure_ascii=False)