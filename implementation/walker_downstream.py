from operator import attrgetter

class WalkerDownstream:
    """
    Knows how to navigate through a Network downstream, emitting events
    corresponding to the Node(s) encountered as it goes. (Visitor Pattern).

    When the walker encounters peer-level choices to recurse into, it navigates
    the choices in alphabetical order (to make the order deterministic and help
    with testing).
    """

    def __init__(self, network, callback):
        """
        The walker will call your callback as it traverses the Network with
        the node as the single argument.
        """
        self._network = network
        self._callback = callback

    def walk_from_terminal(self, terminal):
        """
        Walks downstream from the Terminal you provide.
        """
        for node in self._network.nodes_fed_by_terminal(terminal):
            self.walk_from_node(node)

    def walk_from_node(self, node):
        """
        Walks downstream from the Node you provide (recursively).
        """
        self._callback(node)
        for output_port in sorted(node.output_ports.values(),
                key=attrgetter('name')):
            for node in self._network.nodes_fed_by_output_port(output_port):
                self.walk_from_node(node)


