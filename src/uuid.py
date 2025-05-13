from uuid import uuid4


class UUID:
    def __init__(self):
        self.value = uuid4()
    
    def __hash__(self):
        return hash(self.value)


def update_uuid(uuid):
    uuid.value = uuid4()