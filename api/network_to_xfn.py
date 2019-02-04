

class Network2Xfn:
    """
    This class helps you build networks-of-networks, by letting you *wrap* an
    *existing* network in such a way that it becomes an oven-ready transfer
    function for a node in another *super* network.

    Usage:
        net2xfn = Network2Xfn(existing_net, input_mapping, output_mapping)
        xfn = net2xfn.xfn

    The behaviour you get in the xfn is:

        o  Harvest certain input values from the *input_values_dict* passed
        in at call time
        o  Write these values to the certain terminals on the existing network
        o  Read the values from certain output ports on the existing network.
        o  Write these values back to the super network node using the
           *output_setter_fn* passed in.

    You have to provide the name mappings to use in the *input_mapping* and
    *output_mapping* dictionaries.
    """

    def __init__(self, existing_net, input_mapping, output_mapping):
        """
        :param existing_net: The existing network.
        :param input_mapping: E.g.
            {
                'super_node_input_a': 'existing_net_term_p'
                'super_node_input_b': 'existing_net_term_q'
            }
        :param output_mapping: E.g.
            {
                ('existing_node_X', 'X_output_port_k'): 'super_node_output_s')
                ('existing_node_X', 'X_output_port_m'): 'super_node_output_t')
            }
        """
        self.net = existing_net
        self.input_mapping = input_mapping
        self.output_mapping = output_mapping

    def xfn(self, input_values_dict, output_setter_fn):

        # iterate over input port names and values
        for pname, pvalue in input_values_dict.items():
            # convert a portname to a terminal name
            terminal_name = self.input_mapping[pname]
            # assign port value to appropriate terminal
            self.net.set_terminal_value(terminal_name, pvalue)

        # Unpack the output mapping and get the existing node name,
        # port name and super port name
        for (nname, pname), spname in self.output_mapping.items():
            # get the output value on the output of the existing node
            out = self.net.get_output_port_value(nname, pname)
            # and set it on the output of the super node
            output_setter_fn(spname, out)
