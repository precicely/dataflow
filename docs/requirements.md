# Vision

(See also ../user-manual.md)

> This document saves many words by being written on the assumption that you will
> look first at the simple network diagram at ../reference-network.PNG.

A toolkit to build and operate a data flow **network** where multiple data
inputs pass through a **graph** of interconnected transformation **nodes**,
producing and exposing the transformed **outputs** at each node.

The network once built, may be evaluated **repeatedly** with changed network
input **terminal** values, and will detect automatically which transformations
must be re-applied and which need not be.  This helps the client **avoid the
penalty of needless computationally expensive transformations**.

# Requirements 

- The networks created are *Directed Acyclic Graphs* (DAGs).
- Nodes encapsulate a user defined transfer function (**xfn**).
- Nodes have named input and output **ports**.
- Edges convey an arbitrary object payload from an output port on one node, to an 
  input port on any number of other nodes. (**Fan out**).
- The *Type contract* for edge payloads is a matter for the ports at either 
  end. The toolkit is oblivious to the type of your payloads.

# API Basic Features

- Specify the set of nodes required.
- Specify the xfn for each node.
- Specify the port-to-port edge connectivity.
- Define input terminals for the network, and connect them to node 
  input ports.
- Set values on terminals.
- Read the value from any node output port.

# Stateful Optimisation Contract

Node xfns are evaluated **only** when the client **reads** the value from a node
output port; and then only those on which the output value is dependent.
(recursively).

The read operation fires a side effect, which is that the nodes stores its
resultant output values internally, and marks itself as **clean** (vs **dirty**).
When, subsequently any output of this node is read, while it remains clean, it
will provide its stored value instead of triggering a recursive re-evaluation.

Reciprocally, when the client **writes** a value to a network terminal this
fires a side effect that sets all its downstream nodes to dirty. (recursively).

To summarise the points above:

> Writing to a network terminal propagates *dirty* downstream.
> Reading from a node output propagates *clean* upstream.

# Minimum Coding for the Client

The API must allow the graphs to be configured with minimal client code. In
particular it is desirable that the client need not create sub classes for their
nodes and thus reduce boiler plate. Implying that the client must provide a
xfn callable.

# Error handling Contract

When the toolkit cannot satify the network-building *contract* because of client
side programming errors, it will make this clear and prevent the network from
being used.

When the toolkit can deduce that the network has redundant bits ditto.

# Connections Between Networks

Clients will likely want to construct networks hierarchically, and to re-use
network components.
