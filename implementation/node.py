from operator import attrgetter


from dataflow.implementation.input_port import InputPort
from dataflow.implementation.output_port import OutputPort
from dataflow.api.network_error import NetworkError


class Node:
    """
    A Node in the Network, comprising a set of named InputPorts and OutputPorts,
    and which can hold a client-injected transfer function. Once the ports have
    been set up, and the transfer function injected, the node can be instructed
    to re-evaluate its outputs by calling the execute_transfer_function()
    method.

    It has a state attribute flag called *is_dirty* - which, when set,
    means that the values stored in its output ports, are stale, and must not
    be read. External parties set the dirty flag when they judge necessary, but
    the execute_transfer_function() method sets it back to clean after it has
    completed.
    """

    #------------------------------------------------------------------------
    # API to get the Node set up.
    #------------------------------------------------------------------------
    def __init__(self, name):
        self.input_ports = {}  # InputPort(s) keyed on name.
        self.output_ports = {}  # OutputPort(s) keyed on name.
        self.name = name
        self.is_dirty = True

        self.xfn = None # See set_xfn()

    def register_input_port(self, port_name):
        return self.input_ports.setdefault(
                port_name, InputPort(port_name, self))

    def register_output_port(self, port_name):
        return self.output_ports.setdefault(
                port_name, OutputPort(port_name, self))

    def set_xfn(self, transfer_fn):
        """
        See Network.set_xfn()
        """
        self.xfn = transfer_fn

    #------------------------------------------------------------------------
    # API to execute the transfer function.
    #------------------------------------------------------------------------

    def execute_transfer_function(self):
        # When we call back to the client's transfer function, we provide read
        # access to the input port values by making a dictionary
        # derived from our (private) input ports.
        input_values_dict = self._snapshot_input_values()
        # Similarly, we make it possible for it to write to the output
        # ports by passing it a writer.
        self.xfn(input_values_dict, self._output_setter)
        self.is_dirty = False

    #------------------------------------------------------------------------
    # API with convenience queries.
    #------------------------------------------------------------------------

    def sorted_input_ports(self):
        """
        This Node's input ports, sorted by name.
        """
        return sorted(self.input_ports.values(), key=attrgetter('name'))


    #------------------------------------------------------------------------
    # Private below.
    #------------------------------------------------------------------------

    def _snapshot_input_values(self):
        """
        Makes a dictionary of the current input port values, keyed on port name.
        """
        snapshot = {}
        for name, port in self.input_ports.items():
            snapshot[name] = port.value
        return snapshot

    def _output_setter(self, port_name, value):
        """
        When the network calls a client's transfer function, it provides to that
        function, as an argument, a function they can use to write to this node's
        output ports. This is that function.
        """
        try:
            self.output_ports[port_name].set_value(value)
        except KeyError:
            raise NetworkError(
                'Unknown output port name: <{}> for node: <{}>'.format(
                    port_name, self.name))
