
from dataflow.api.network_factory import NetworkFactory

REF_SCRIPT = """
    # I am a comment
    TERM:X          > adder:in_1
                    > multiplier:in_1
    TERM:Y          > adder:in_2
                    > multiplier:in_2   # I am a comment too.
    adder:sum       > formatter:in_1
    multiplier:prod > formatter:in_2
    formatter:msg   > DANGLING
"""


def build_reference_network():
    """
    Builds a reference network.
    :return:
    """
    builder = NetworkFactory(REF_SCRIPT)
    net = builder.build()
    net.set_xfn('adder', adder_xfn)
    net.set_xfn('multiplier', mult_xfn)
    net.set_xfn('formatter', format_xfn)
    return net


def adder_xfn(input_values_dict, output_setter_fn):
    in_1 = input_values_dict['in_1']
    in_2 = input_values_dict['in_2']
    output_setter_fn('sum', in_1 + in_2)


def mult_xfn(input_values_dict, output_setter_fn):
    in_1 = input_values_dict['in_1']
    in_2 = input_values_dict['in_2']
    output_setter_fn('prod', in_1 * in_2)


def format_xfn(input_values_dict, output_setter_fn):
    in_1 = input_values_dict['in_1']
    in_2 = input_values_dict['in_2']
    formatted = 'sum: {}, mult: {}'.format(str(in_1), str(in_2))
    output_setter_fn('msg', formatted)
