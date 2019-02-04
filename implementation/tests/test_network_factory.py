
import unittest

from dataflow.api.network_factory import NetworkFactory
from dataflow.implementation.reference_network import REF_SCRIPT


class TestNetworkFactory(unittest.TestCase):

    def test_it_runs(self):
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()
        self.assertIsNotNone(net, 'Builder returned None')
