
class OutputPort:
    """
    """

    def __init__(self, name, node):
        self.node = node
        self.name = name
        self._value = None

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value
