
class InputPort:
    """
    """
    # Todo consider merit of input ports and outputs sharing memory for their
    #  value. Plus does this challenge edges?
    # todo, also it's not quite NICE that ports know what node they belong to.
    def __init__(self, name, node):
        self.node = node
        self.name = name
