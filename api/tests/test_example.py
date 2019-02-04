
import unittest

from dataflow.implementation.reference_network import build_reference_network


class TestExample(unittest.TestCase):

    def test_demonstrate_reference_example(self):
        # Build the reference network.
        net = build_reference_network()

        # Write some values to the network's terminals.
        net.set_terminal_value('X', 42)
        net.set_terminal_value('Y', 3.14)

        # Query the most downstream node output, (which will stimulate a 
        # recursive evaluation of the transfer functions.)
        msg = net.get_output_port_value('formatter', 'msg')
        self.assertEqual(msg, 'sum: 45.14, mult: 131.88',
                'Wrong output from Network')
