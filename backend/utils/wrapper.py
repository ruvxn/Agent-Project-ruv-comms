from copy import deepcopy
from functools import wraps


def node_log(node_function):
    @wraps(node_function)
    def wrapper(state, *args, **kwargs):
        if not hasattr(state, "logs"):
            state.logs = []

        state.logs.append(f"{node_function.__name__} called")
        new_state = node_function(state, *args, **kwargs)
        print(new_state.logs[-1])
        return new_state
    return wrapper
