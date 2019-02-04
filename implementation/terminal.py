
class Terminal:
    """
    An input terminal for a Network.
    Clients can set it's value with the write_value() method, each invocation
    of which causes an event to be emitted to subscribed clients.
    """

    def __init__(self, name):
        self.name = name
        self.value = None
