
import unittest

from dataflow.api.network_factory import NetworkFactory
from dataflow.implementation.reference_network import REF_SCRIPT
from dataflow.implementation.walker_downstream import WalkerDownstream


class TestWalkerDownstream(unittest.TestCase):

    def setUp(self):
        builder = NetworkFactory(REF_SCRIPT)
        self.net = builder.build()

    def test_walk_from_node(self):
        node = self.net.nodes['adder']
        monitor = Monitor()
        WalkerDownstream(self.net, monitor.callback).walk_from_node(node)
        self.assertEqual(
            monitor.node_names, ['adder', 'formatter'], 'Wrong nodes from walker.')

    def test_walk_from_terminal(self):
        terminal = self.net.terminals['X']
        monitor = Monitor()
        WalkerDownstream(self.net, monitor.callback).walk_from_terminal(terminal)
        self.assertEqual(
            monitor.node_names,
            ['adder', 'formatter', 'multiplier', 'formatter'],
            'Wrong nodes from walker.')

class Monitor:

    def __init__(self):
        self.node_names = []

    def callback(self, node):
        self.node_names.append(node.name)