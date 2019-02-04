
class Edge:
    """
    """

    def __init__(self, source, dest):
        """
        Source should be either a Terminal or an OutputPort.
        Dest should be an InputPort
        """
        self.source = source
        self.dest = dest
