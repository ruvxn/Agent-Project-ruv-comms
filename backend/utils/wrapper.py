from copy import deepcopy
from functools import wraps


def node_log(node_function):
    @wraps(node_function)
    def wrapper(state, *args, **kwargs):
        if not hasattr(state, "message"):
            state.message = []

        log_messages = []
        log_messages.append(f"{node_function.__name__} called")

        new_state = node_function(state, *args, **kwargs)

        # log_messages.append(f"state after call: {new_state}")
        new_state.message.extend(log_messages)
        print(new_state.message[-1])
        return new_state
    return wrapper
