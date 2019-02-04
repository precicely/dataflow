from dataflow.implementation.walker_downstream import WalkerDownstream

class DirtyPropagator:
    """
    Takes responsibility for propagating a dirty status downstream from a
    terminal to all dependent downstream nodes recursively.
    """

    def __init__(self, graph):
        self._graph = graph

    def propagate(self, terminal):
        # Use a visitor to traverse the dependencies, with a callback
        # that does the 'dirty' work.
        callback = lambda node: setattr(node, 'is_dirty', True)
        walker = WalkerDownstream(self._graph, callback)
        walker.walk_from_terminal(terminal)
