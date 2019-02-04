
import unittest

from dataflow.api.network_factory import NetworkFactory
from dataflow.implementation.reference_network import REF_SCRIPT


class TestUsingClassMethodAsXfnCallback(unittest.TestCase):

    def test_using_class_method_as_xfn_callback(self):
        builder = NetworkFactory(REF_SCRIPT)
        net = builder.build()

        # Two plain function callbacks
        net.set_xfn('adder', self.adder_xfn)
        net.set_xfn('multiplier', self.mult_xfn)

        # One class-method callback
        formatter = FormatterNodeXfn()
        net.set_xfn('formatter', formatter.xfn_callback)

        # Write some values to the network's terminals.
        net.set_terminal_value('X', 42)
        net.set_terminal_value('Y', 3.14)

        # Query the most downstream node output, (which will stimulate a 
        # recursive evaluation of the transfer functions.)
        msg = net.get_output_port_value('formatter', 'msg')
        self.assertEqual('sum: 45.14, mult: 131.88', msg,
                'Wrong output from Network')

    #--------------------------------------------------------------------------
    # The example transfer functions.
    #--------------------------------------------------------------------------

    def adder_xfn(self, input_values_dict, output_setter_fn):
        in_1 = input_values_dict['in_1']
        in_2 = input_values_dict['in_2']
        output_setter_fn('sum', in_1 + in_2)

    def mult_xfn(self, input_values_dict, output_setter_fn):
        in_1 = input_values_dict['in_1']
        in_2 = input_values_dict['in_2']
        output_setter_fn('prod', in_1 * in_2)

class FormatterNodeXfn:

    def __init__(self):
        # Give the object some state, to show that it is reachable
        # by the xfn callback at call-time.
        self.some_state = 'hello! Ding dong!'

    def xfn_callback(self, input_values_dict, output_setter_fn):
        # Proof that I can access the state held in the node object here
        # to help with implementing the callback logic.
        assert(self.some_state == 'hello! Ding dong!')

        # The same transfer function logic as the old function-based
        # implementation.
        in_1 = input_values_dict['in_1']
        in_2 = input_values_dict['in_2']
        formatted = 'sum: {}, mult: {}'.format(str(in_1), str(in_2))
        output_setter_fn('msg', formatted)
