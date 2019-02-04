from operator import attrgetter


from dataflow.implementation.input_port import InputPort
from dataflow.implementation.output_port import OutputPort
from dataflow.api.network_error import NetworkError


class NetworkIntegrity:
    """
    Offers a checking service to see if there is something fishy about a network.
    Like a node having an unused input port, or not having a transfer function 
    and similar.

    It follows that it CANNOT be used until the client has injected the transfer
    functions, and this is why it isn't used by the NetworkBuilder.

    Usage:

        NetworkIntegrity.check_now(network)

    Raises NetworkError when it finds a problem.
    """

    @classmethod
    def check_now(cls, network):
        cls._assert_no_missing_xfns(network)
        cls._assert_no_unset_terminals(network)

    #------------------------------------------------------------------------
    # Private below.
    #------------------------------------------------------------------------

    @classmethod 
    def _assert_no_missing_xfns(cls, network):
        """
        See if the there any nodes in the network, that haven't been given
        a transfer function.
        """
        for node_name, node in network.nodes.items():
            if node.xfn is None:
                raise NetworkError(
                    ('No transfer function has been set for your node '
                    'called <{}>.').format(node_name))

    @classmethod 
    def _assert_no_unset_terminals(cls, network):
        """
        See if the there any terminals in the network, which haven't had their
        value set yet.
        """
        for terminal_name, terminal in network.terminals.items():
            if terminal.value is None:
                raise NetworkError(
                    ('No value has been been set for your terminal '
                    'called <{}>.').format(terminal_name))

