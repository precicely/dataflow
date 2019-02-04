import unittest

from dataflow.api.network_error import NetworkError
from dataflow.api.network_factory import NetworkFactory
from dataflow.implementation.reference_network import REF_SCRIPT


class TestErrorHandling(unittest.TestCase):

    def test_exceptions_raised_by_set_terminal_value(self):
        """
        Make sure that calling net.set_terminal_value() with a non
        existent terminal name produces the intended exception.
        """
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()

        with self.assertRaises(NetworkError) as cm:
            net.set_terminal_value('fibble', 42)
        self.assertEqual('Unknown terminal name: <fibble>', 
                        str(cm.exception), 'Wrong message.')

    def test_exceptions_raised_by_set_xfn(self):
        """
        Make sure that calling net.set_xfn() with a non
        existent node name produces the intended exception.
        """
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()

        with self.assertRaises(NetworkError) as cm:
            net.set_xfn('fibble', None)
        self.assertEqual('Unknown node name: <fibble>', 
                            str(cm.exception), 'Wrong message.')

    def test_exceptions_raised_by_output_setter_fn(self):
        """
        Make sure that when a client-supplied transfer function uses
        the output_setter_fn() provided to it, and calls it with a non 
        existent output port name, the intended exception is raised.
        """
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()

        # This is our naughty transfer function. It tries to write to a port
        # called 'fibble', which does not exist.
        def xfn(input_values_dict, output_setter_fn):
            in_1 = input_values_dict['in_1']
            in_2 = input_values_dict['in_2']
            output_setter_fn('fibble', None)

        net.set_xfn('adder', xfn)
        net.set_xfn('multiplier', xfn)
        net.set_xfn('formatter', xfn)

        net.set_terminal_value('X', 42)
        net.set_terminal_value('Y', 3.14)

        # Here we stimulate (implicitly) the transfer function and expect the 
        # exception to be raised.
        with self.assertRaises(NetworkError) as cm:
            msg = net.get_output_port_value('formatter', 'msg')
        self.assertEqual('Unknown output port name: <fibble>', 
                            str(cm.exception), 'Wrong message.')

    def test_exceptions_raised_by_get_output_port_value(self):
        """
        Make sure that when the client tries to read an output port that does
        not exist, it produces the intended exception.
        """
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()

        xfn = lambda input_values_dict, output_setter_fn: None

        net.set_xfn('adder', xfn)
        net.set_xfn('multiplier', xfn)
        net.set_xfn('formatter', xfn)

        net.set_terminal_value('X', 42)
        net.set_terminal_value('Y', 3.14)

        # No such node
        with self.assertRaises(NetworkError) as cm:
            msg = net.get_output_port_value('fibble', 'msg')
        self.assertEqual('Unknown node name: <fibble>', 
                str(cm.exception), 'Wrong message.')
        # No such port
        with self.assertRaises(NetworkError) as cm:
            msg = net.get_output_port_value('formatter', 'fibble')
        self.assertEqual(
            'Node: <formatter> does not have an output port called: <fibble>', 
            str(cm.exception), 'Wrong message.')

    def test_integrity_check_fires_on_read_and_detects_missing_xfn(self):
        """
        Make sure that when the client tries to read an output port, the internal
        network integrity check fires, and properly detects when there is a node
        that has no transfer function.
        """
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()
        xfn = lambda input_values_dict, output_setter_fn: None
        # We omit setting the xfn for 'adder'.
        net.set_xfn('multiplier', xfn)
        net.set_xfn('formatter', xfn)
        net.set_terminal_value('X', 42)
        net.set_terminal_value('Y', 3.14)
        with self.assertRaises(NetworkError) as cm:
            msg = net.get_output_port_value('formatter', 'msg')
        self.assertEqual(
            'No transfer function has been set for your node called <adder>.',
            str(cm.exception), 'Wrong message.')

    def test_integrity_check_fires_on_read_and_detects_unset_terminals(self):
        """
        Make sure that when the client tries to read an output port, the internal
        network integrity check fires, and properly detects when there is a
        terminal for which no value has yet been set.
        """
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()
        xfn = lambda input_values_dict, output_setter_fn: None
        net.set_xfn('adder', xfn)
        net.set_xfn('multiplier', xfn)
        net.set_xfn('formatter', xfn)
        net.set_terminal_value('X', 42)
        # We omit setting the value of terminal Y
        with self.assertRaises(NetworkError) as cm:
            msg = net.get_output_port_value('formatter', 'msg')
        self.assertEqual(
            'No value has been been set for your terminal called <Y>.',
            str(cm.exception), 'Wrong message.')
