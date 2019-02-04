# User Manual for dataflow Package

(See also ../requirements.md)

- This document explains how you build networks and how you operate them.
- It includes code fragments to introduce you to it one bit at a time.
- You can see it all joined up in dataflow/api/tests/test_example.py
- Again refer to ../reference-network.PNG since this is the network we build.

# Script language

You build a network using a simple domain specific language, like this:

    from dataflow.api.network_factory import NetworkFactory

    builder = NetworkFactory("""
        TERM:X          > adder:in_1
                        > multiplier:in_1
        TERM:Y          > adder:in_2
                        > multiplier:in_2
        adder:sum       > formatter:in_1
        multiplier:prod > formatter:in_2
        formatter:msg   > DANGLING
    """)
    net = builder.build()

This script example is interpreted as follows:

> The network has a terminal called X, which is routed to an input port
> called in_1 on a node called adder, and also to an input port called in_1 on
> a node called multiplier.
>
> The second line is of the same pattern.
> 
> The adder node has an output port called sum, which is routed to an input port
> called in_1 on a node called formatter.
> 
> The formatter node has an output port called msg, which is not routed anywhere.
> 
> Nb. TERM and DANGLING are reserved words.

# Injecting the Transfer Functions for Nodes

The network now has nodes, terminals, input and output ports, and is *wired up*.
But the nodes have no computational **behaviour** defined.

You inject the behaviour by providing transfer functions like this:

    net.set_xfn('adder', your_xfn)

The network will call *your_xfn* when it needs to refresh the adder node's 
outputs.

The signature provides you with a way to look up the node's current input port 
values, and a way to send back your calculated outputs:

    your_xfn(input_values_dict, output_setter_callback)

You read the inputs like this:

    foo = input_values_dict['in_1']

And you send back your outputs like this:

    output_setter_callback('sum', 56.3)

# Operating your Network

## Initialise the Terminal Values

First you must initialise the values on the network's input terminals:
We use numbers in the example, but these can be any type of object you choose.

    net.set_terminal_value('X', 42)
    net.set_terminal_value('Y', 3.14)

> Note this step does **not** trigger any node transfer functions in of itself.

## Simply Now Read an Output Port Value

    print(net.output_value('formatter', 'msg'))

It is this **read** operation that will trigger internally the evaluation of all
the necessary node transfer functions. The network will have determined that this
particular output is dependent on all the nodes, and so will have triggered the
transfer functions on all of the nodes.

# Change one of the Terminal's Values

You can change the input terminal values any time you like, and continue to read
any outputs you like. Whenever you mutate terminal values, the network keeps 
track (internally) of which nodes are affected (including downstream dependents).
Then we when you read outputs, it knows which nodes must re-evaluate their
transfer functions and which need not.

> This example network cannot exploit this optimisation - because all nodes are
> dependent on both terminals.

    net.set_terminal_value('X', 43)
    print(net.output_value('formatter', 'msg'))

# Access Outputs from Intermediate Nodes

You can access the output ports of every node.

    print(net.output_value('adder', 'sum'))

# Features not Obvious from the Example Network

- Nodes can have as many output ports as you want.
- Terminals can be wired up to the input ports of any node.
- You can easily make networks-of-networks (see below).

# Transfer Functions that Need Their Own State to Work
If you want to have state available in your transfer function use an object
instance  method as your transfer function. That way when it gets called-back to,
it has access to to *self*. See a simple example:

    api/tests/test_using_class_method_as_xfn_callback.py

# Interconnecting and Reusing Networks
You can nest networks by using an existing complete network as a node in 
another network. There is a helper class to make this easy to do. 

    from dataflow.api.network_xfn import Network2Xfn

You construct it providing the network you want to treat thus, and trivial
dictionaries that tell it how to *wire it up*. It then exposes an *oven-ready*
transfer function you can use in your super network.

See the example usage in this test:

    dataflow.api.tests.text_network_to_xfn.py
