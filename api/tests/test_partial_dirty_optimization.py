
import unittest

from dataflow.api.network_factory import NetworkFactory


class TestPartialDirtyOptimization(unittest.TestCase):
    """
    This test checks that needless node re-evaluations are skipped as they
    should be when possible.
    """

    def test_partial_dirty_optimization(self):
        #  This script makes a linear daisy-chain of three almost identical nodes
        #  A,B,C. They are daisy chained together so that we can we can mutate
        #  a terminal that feeds B, and make sure B and C get re-evaluated,
        #  while A does not.

        # Every node has two input ports *operand* (just a number), and *scale'.
        # They multiply their operand by the scale and write the result to an
        # output port called *result*. It is the result that is daisy-chained
        # to the next node's *operand*.
        # The scale input for all of them comes from a separate network
        # terminal dedicated to each of them.
        # Node A exposes a terminal to sekt its operand at the beginning of the
        # chain.

        script = """
            TERM:scale_A > A:scale
            TERM:scale_B > B:scale
            TERM:scale_C > C:scale

            TERM:op_A    > A:op

            A:result     > B:op
            B:result     > C:op
            C:result     > DANGLING
        """
        builder = NetworkFactory(script)
        net = builder.build()

        # Inject the transfer functions.
        scaler = ScalerXfn()
        net.set_xfn('A', scaler.xfn_callback)
        net.set_xfn('B', scaler.xfn_callback)
        net.set_xfn('C', scaler.xfn_callback)

        # Initialise all the terminals.

        net.set_terminal_value('scale_A', 2)
        net.set_terminal_value('scale_B', 3)
        net.set_terminal_value('scale_C', 4)
        net.set_terminal_value('op_A', 100)

        # Read C's result to make all of the nodes clean.
        output_of_c = net.get_output_port_value('C', 'result')
        self.assertEqual(2400, output_of_c, 'Wrong output from Network')

        # Now make sure we only get the correct two evaluation 'fires' when
        # we mutate the scale-setting terminal for B.
        net.set_terminal_value('scale_B', 4)
        output_of_c = net.get_output_port_value('C', 'result')
        self.assertEqual(3200, output_of_c, 'Wrong output from Network')
        self.assertEqual(5, scaler.fired_count,'Wrong number of calls.')


class ScalerXfn:
    """
    We have made the Node transfer function a member function of a class, so
    that the object can keep track of how many times it gets called.
    """

    def __init__(self):
        self.fired_count = 0

    def xfn_callback(self, input_values_dict, output_setter_fn):
        operand = input_values_dict['op']
        scale = input_values_dict['scale']
        output_setter_fn('result', operand * scale)
        # This xfn counts how many times it is fired.
        self.fired_count += 1




