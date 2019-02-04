
import unittest
from dataflow.api.network_factory import NetworkFactory
from dataflow.implementation.reference_network import build_reference_network
from dataflow.api.network_to_xfn import Network2Xfn

_TEST_SCRIPT = """
    TERM:A                    > NetworkInANode:A
    TERM:B                    > NetworkInANode:B
    NetworkInANode:sentence > DANGLING

"""

class TestNetwork2Xfn(unittest.TestCase):
    """
    Tests the automatic conversion of a network into a single transfer function.

    It does this by providing an input and output mapping dictionary to
    convert the network's terminal names to appropriate input an node names.
    The same is true of the outputs.
    """

    def test_xfn(self):
        ref_net = build_reference_network()
        input_mapping = {'A': 'X', 'B': 'Y'}
        output_mapping = {('formatter', 'msg'): 'sentence'}
        net2xfn = Network2Xfn(ref_net, input_mapping, output_mapping)

        builder = NetworkFactory(_TEST_SCRIPT)
        net = builder.build()
        net.set_xfn('NetworkInANode', net2xfn.xfn)
        net.set_terminal_value('A', 42)
        net.set_terminal_value('B', 3.14)
        sentence = net.get_output_port_value('NetworkInANode', 'sentence')

        self.assertEqual('sum: 45.14, mult: 131.88', sentence,
                         'Unexpected output')
