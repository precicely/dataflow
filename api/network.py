from operator import attrgetter


from dataflow.api.network_error import NetworkError
from dataflow.implementation.node import Node
from dataflow.implementation.terminal import Terminal
from dataflow.implementation.edge import Edge
from dataflow.implementation.dirty_propagator import DirtyPropagator
from dataflow.implementation.network_integrity import NetworkIntegrity


class Network:
    """
    This is the public API to this package.
    It Is-A complete graph instance model.
    Clients from outside this package should interact only using the exposed
    methods, (not the exposed attributes). The latter are exposed only for
    sister modules in the same package.
    """


    def __init__(self):
        # The following dicts comprise storage for the graph artefacts,
        # and are all keyed on the member names.
        self.nodes = {}
        self.terminals = {}
        self.edges = []

        # A helper that knows how to propagate dirty status downstream.
        self._dirty_propagator = DirtyPropagator(self)

    # ------------------------------------------------------------------------
    # Network Creation API
    # ------------------------------------------------------------------------

    def register_node(self, name):
        self.nodes.setdefault(name, Node(name))

    def register_terminal(self, name):
        # Do nothing if it already exists?
        if name in self.terminals:
            return self.terminals[name]
        # Otherwise create and register it.
        self.terminals[name] = Terminal(name)

    def register_input_port(self, node_name, port_name):
        node = self.nodes[node_name]
        node.register_input_port(port_name)

    def register_output_port(self, node_name, port_name):
        node = self.nodes[node_name]
        node.register_output_port(port_name)

    def create_terminal_edge(self, terminal_name, downstream_node_name,
                             downstream_port_name):
        terminal = self.terminals[terminal_name]
        node = self.nodes[downstream_node_name]
        port = node.input_ports[downstream_port_name]
        self._assert_not_duplicate_edge(terminal, port)
        self.edges.append(Edge(terminal, port))

    def create_output_to_input_edge(self,
                upstream_node_name, upstream_port_name,
                downstream_node_name, downstream_port_name):
        u_node = self.nodes[upstream_node_name]
        u_port = u_node.output_ports[upstream_port_name]
        d_node = self.nodes[downstream_node_name]
        d_port = d_node.input_ports[downstream_port_name]
        self._assert_not_duplicate_edge(u_port, d_port)
        self.edges.append(Edge(u_port, d_port))

    def set_xfn(self, node_name, transfer_fn):
        """
        The is the method the client uses to provide a node's evaluation
        function. It will be called back by the Network when it needs to
        refresh the Node's outputs. The signature of the callback looks like
        this:

            your_callback(input_values_dict, output_setter_callback)

        So your your_callback can read the current values of input ports
        like this:

            foo = input_values_dict['in_1']

        And it is obliged to set the values on output ports like this:

            output_setter_callback('sum', 56.3)
        """
        # Delegate to the node.
        try:
            self.nodes[node_name].set_xfn(transfer_fn)
        except KeyError:
            raise NetworkError('Unknown node name: <{}>'.format(node_name))


    #------------------------------------------------------------------------
    # Network Operation API
    #------------------------------------------------------------------------

    def set_terminal_value(self, terminal_name, value):
        """
        This is where the client can write a value to one of the Network's
        input terminals. Which in turn, stimulates the propagation of a dirty
        status to all the dependent nodes downstream.
        """
        try:
            terminal = self.terminals[terminal_name]
            terminal.value = value
            self._dirty_propagator.propagate(terminal)
        except KeyError:
            raise NetworkError(
                'Unknown terminal name: <{}>'.format(terminal_name))

    def get_output_port_value(self, node_name, output_port_name):
        """
        This is where the client can read a value from a node's output terminal,
        which in turn stimulates a recursive upstream re-evaluation of its
        inputs if necessary.
        """
        # First fire the network integrity checker, and then all being well,
        # (it doesn't raise an exception), continue to answer the question.
        NetworkIntegrity.check_now(self)

        # We do the real (recursive) work in a private implementaton function, so
        # that we can avoid the cost of repeated integrity checks every time it
        # recurses.
        return self._get_output_port_value(node_name, output_port_name)


    #------------------------------------------------------------------------
    # Network Queries
    #------------------------------------------------------------------------

    # #todo these should not be available in the public API !!!
    def nodes_fed_by_terminal(self, terminal):
        """
        To which Node(s) is the given Terminal routed?
        (sorted alphabetically).
        """
        edges = [e for e in self.edges if e.source == terminal]
        input_ports = [e.dest for e in edges]
        return sorted([port.node for port in input_ports],
                       key=attrgetter('name'))

    def nodes_fed_by_output_port(self, output_port):
        """
        Which nodes are fed by the given output port?
        (Sorted alphabetidally).
        """
        edges = [e for e in self.edges if e.source == output_port]
        input_ports = [e.dest for e in edges]
        return sorted([port.node for port in input_ports],
                       key=attrgetter('name'))

    def edge_for_input(self, input_port):
        for edge in self.edges:
            if edge.dest == input_port:
                return edge
        raise RuntimeError('Cannot find edge for input port: {}.{}'.format(
            input_port.node.name, input_port.name))
    #------------------------------------------------------------------------
    # Private below.
    #------------------------------------------------------------------------

    def _assert_not_duplicate_edge(self, source, dest):
        for edge in self.edges:
            if (edge.source == source) and (edge.dest == dest):
                raise RuntimeError(
                    'Encountered duplicate edge from: {} to {}'.format(
                        source.name, dest.name))

    def _get_output_port_value(self, node_name, output_port_name):
        """
        This is the private implementation for get_output_port().
        It is isolated from the public method, so that the public method
        can make a network integrity check before it gets going with the
        (recursive) real work.
        """
        # Get hold of the node/port objects - (with error handling)
        try:
            node = self.nodes[node_name]
        except KeyError:
            raise NetworkError(
                'Unknown node name: <{}>'.format(node_name))
        try:
            output_port = node.output_ports[output_port_name]
        except KeyError:
            raise NetworkError(
                'Node: <{}> does not have an output port called: <{}>'.format(
                    node_name, output_port_name))

        # If the node is clean - we can simpy return the output port's
        # saved value.
        if not node.is_dirty:
            return output_port.get_value()
        # Otherwise we must re-fetch the latest imports (recursively).
        # todo can we make the back/fwd propagation read as more symmetrical?
        self._refresh_inputs_recursively(node)
        # Now we can re-evaluate our own outputs, by invoking the transfer
        # function. This autonomously sets the node to being clean again.
        node.execute_transfer_function()
        return output_port.get_value()


    def _refresh_inputs_recursively(self, node):
        """
        Knows how to traverse the input ports on the given node, and fetch the
        values for them from whichever output ports (and/or terminals) that is
        feeding them. It does this using a recursive call to
        _get_output_port_value(), thus propagating the process back upstream as
        far as is necessary.
        """
        # The traversal order for input ports is arbitrary, but we make it
        # repeatable to assist in debugging and testing.
        for input_port in node.sorted_input_ports():
            incoming_edge = self.edge_for_input(input_port)
            upstream_obj = incoming_edge.source
            # Behaviour depends on if its a Terminal or OutputPort
            if isinstance(upstream_obj, Terminal):
                input_port.value = upstream_obj.value
            else:
                # The recursive call...
                output_port = upstream_obj
                input_port.value = self._get_output_port_value(
                    output_port.node.name, output_port.name)
