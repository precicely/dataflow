
import unittest

from dataflow.api.network_factory import NetworkFactory
from dataflow.implementation.reference_network import REF_SCRIPT


class TestNetworkCreationErrorHandling(unittest.TestCase):

    def test_todo(self):
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()

