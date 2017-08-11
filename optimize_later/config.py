callbacks = []


def register_callback(callback):
    callbacks.append(callback)
    return callback


def deregister_callback(callback):
    callbacks.remove(callback)
