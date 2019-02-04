from unittest import TestCase

from dataflow.api.network_factory import NetworkFactory
from dataflow.implementation.reference_network import REF_SCRIPT


class TestDirtyPropagator(TestCase):

    def setUp(self):
        builder = NetworkFactory(REF_SCRIPT)
        self.net = builder.build()

    def test_dirty_propagation(self):
        # Artificially set all nodes to clean
        for node in self.net.nodes.values():
            node.is_dirty = False
        # Write to a terminal and then inspect that the right nodes have
        # been set to dirty.
        self.net.set_terminal_value('X', 42)
        are_set = [node for node in self.net.nodes.values() if node.is_dirty]
        dirty_names = sorted([node.name for node in are_set])
        self.assertEqual(dirty_names, ['adder', 'formatter', 'multiplier'],
                'Wrong reply from which_nodes_are_dirty()')


