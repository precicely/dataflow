import re


from dataflow.api.network import Network

class NetworkFactory:
    """
    Builds a Network from a script string.
    """

    def __init__(self, script:str):
        self._script = script
        # Keep track of most recently encountered left hand side segment
        # to be used by continuation lines.
        self._saved_lhs = None

    def build(self):
        net = Network()
        # Deal with one line of the script at a time - incrementally updating
        # The Network as it goes.
        for line in self._script.splitlines():
            self._action_one_line(line, net)
        return net

    #---------------------------------------------------------------------------
    # Private below.
    #---------------------------------------------------------------------------

    def _action_one_line(self, line, net):
        """
        Interprets and actions one line of the script.
        """

        # Line types to handle.

        # I am a comment.
        # TERM:X          > adder:in_1          # canonical (terminal->in)
        #                 > multiplier:in_1     # continuation
        # adder:sum       > formatter:in_1      # canonical (out->in)
        # formatter:msg   > DANGLING            # Dangling

        line = self._remove_comment(line)
        line = line.strip()
        if len(line) == 0:
            return
        left, right = self._split_into_two(line, '>', line)
        if left == "":
            self._action_continuation_line(right, line, net)
            return
        self._saved_lhs = left
        if right == 'DANGLING':
            self._action_dangling_line(left, line, net)
        else:
            self._action_canonical_line(left, right, line, net)

    def _action_canonical_line(self, left, right, line, net):
        """
        Handles these two variants:
            TERM:X          > adder:in_1
            adder:sum       > formatter:in_1
        """
        upstream_node_name, upstream_port_name = \
            self._split_into_two(left, ':', line)
        downstream_node_name, downstream_port_name = \
            self._split_into_two(right, ':', line)

        net.register_node(downstream_node_name)
        net.register_input_port(downstream_node_name, downstream_port_name)

        if upstream_node_name == self._RW_TERM:
            net.register_terminal(upstream_port_name)
            net.create_terminal_edge(
                upstream_port_name, downstream_node_name, downstream_port_name)
        else:
            net.register_node(upstream_node_name)
            net.register_output_port(upstream_node_name, upstream_port_name)
            net.create_output_to_input_edge(
                upstream_node_name, upstream_port_name, downstream_node_name,
                downstream_port_name)

    def _action_dangling_line(self, left, line, net):
        """
        Handles: 
            formatter:msg   > DANGLING
        """
        node_name, port_name = self._split_into_two(left, ':', line)
        net.register_node(node_name)
        net.register_output_port(node_name, port_name)

    def _action_continuation_line(self, right, line, net):
        if self._saved_lhs is None:
            raise ParseError('A line with a left-hand-side must '
                    'exist before this dangline line is used |{}|.'.format(line))
        implied_left = self._saved_lhs
        self._action_canonical_line(implied_left, right, line, net)

    def _split_into_two(self, buf, delim, line):
        """
        Split the string buf into two pieces using the given delimiter.
        Returns the two (stripped) pieces as a tuple, or raises ParseError.
        """
        left_and_right = [s.strip() for s in buf.split(delim)]
        if len(left_and_right) != 2:
            raise ParseError(
                'Cannot split this part |{}| of this line |{}| ' 
                'into two using |{}|'.format(buf, line, delim))
        return left_and_right


    def _remove_comment(self, line):
        """
        Return a copy of <line>, having removed from it anything beyond
        a # character. (Including the # itself).
        """
        return re.sub(r'#.*', "", line)

    _RW_TERM = 'TERM'

class ParseError(Exception):
    pass

