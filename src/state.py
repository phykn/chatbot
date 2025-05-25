from uuid import uuid4


class State:
    def __init__(self):
        self.value = uuid4()


def update_state(state):
    state.value = uuid4()