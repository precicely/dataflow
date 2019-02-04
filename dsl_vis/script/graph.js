/**
 * The Graph class is used to represent data flow graphs.
 * It implements a DSL parser, and can export the graph
 * into ELKjs JSON.
 * 
 * A graph visual representation is defined by its nodes, which can be one of three types:
 * node, terminal and dangling.
 * Each node can have input and output ports, which can be connected.
 */
Graph = (function() {

    function Graph() {
        if (!(this instanceof Graph)) {
            return new Graph();
        }

        this._nodes = {};
        this._connections = [];
    }

    /**
     * Add a node if it does not exist, or do nothing otherwise.
     * This function can be called several times on the same node
     * to add ports of different types (input and output).
     * @param id Node ID 
     * @param ports List of port names (IDs)
     * @param port_type Type of ports.
     */
    Graph.prototype.touchNode = function(id, ports, port_type) {
        var type = 'node'
        var label = id;
        if (id == 'TERM') {
            id = 'TERM_' + ports[0];
            type = 'terminal';
            label = ports[0];
        } else if (id == 'DANGLING') {
            id = 'DANG_' + ports[0];
            type = 'dangling';
            label = ports[0];
        }
        var node = {}
        if (id in this._nodes) {
            node = this._nodes[id];
        } else {
            node['id'] = id;
            node['label'] = label;
            node['ports'] = {};
            node['type'] = type;
            this._nodes[id] = node;
        }

        for (var i = 0; i < ports.length; i++) {
            var port = ports[i];
            var id = port + '_' + port_type;
            if (!(id in node['ports'])) {
                var new_port = {}
                new_port['id'] = id;
                new_port['node'] = node;
                new_port['type'] = port_type
                new_port['label'] = port;
                node['ports'][id] = new_port;
            }
        }

        return node;
    }

    /**
     * Establish a connection between two nodes, ports.
     * This method will create nodes and ports if required.
     * Port types are deduces from whether a port is a source (output)
     * or a destination (input) of this connection.
     * @param source_node_id Source node ID
     * @param source_port_id Source port ID
     * @param target_node_id Target node ID
     * @param target_port_id Target port ID
     */
    Graph.prototype.connect = function(source_node_id, source_port_id, target_node_id, target_port_id) {
        var source_node = this.touchNode(source_node_id, [source_port_id], 'output');
        var target_node = this.touchNode(target_node_id, [target_port_id], 'input');
        var connection = {
            source: source_node['ports'][source_port_id + '_output'],
            target: target_node['ports'][target_port_id + '_input']
        }
        this._connections.push(connection);
    }

    /**
     * Reset the graph by deleting all nodes and connections.
     */
    Graph.prototype.reset = function() {
        this._nodes = {};
        this._connections = [];
    }

    /**
     * Parse DSL string.
     * @param str String to parse
     * @param error_callback Function that will be called on syntax error. This function
     * should take two arguments: line number, and error message string.
     */
    Graph.prototype.parse = function(str, error_callback) {
        var lines = str.split("\n");
        var src_node = null;
        var src_port = '';
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i].trim();
            if (line.length > 0) {
                if (line.substring(0, 1) != '#') {
                    var nodes = line.split('>');
                    if (nodes.length == 2) {
                        var src = nodes[0].trim();
                        var dst= nodes[1].trim();
                        if (src.length == 0) {
                            // Continuation of previous connection
                            if (src_node == null) {
                                error_callback(i, "Source node is missing");
                                return false;                                
                            }
                        } else {
                            var parts = src.split(":");
                            if (parts.length != 2) {
                                error_callback(i, "Invalid source identifier: " + src);
                                return false;
                            }
                            src_node = parts[0].trim();
                            src_port = parts[1].trim();
                        }
                        if (dst == 'DANGLING') {
                            var dst_node = "DANGLING";
                            var dst_port = src_node + ':' + src_port;
                        } else {
                            var parts = dst.split(":");
                            if (parts.length != 2) {
                                error_callback(i, "Invalid destination identifier: " + dst);
                                return false;
                            }
                            dst_node = parts[0].trim();
                            dst_port = parts[1].trim();
                        }

                        if (src_node.length == 0) {
                            error_callback(i, "Expected source node identifier");
                            return false;
                        }
                        if (src_port.length == 0) {
                            error_callback(i, "Expected source node output port identifier");
                            return false;
                        }
                        if (dst_node.length == 0) {
                            error_callback(i, "Expected destination node identifier");
                            return false;
                        }
                        if (dst_port.length == 0) {
                            error_callback(i, "Expected destination node port identifier");
                            return false;
                        }
                        this.connect(src_node, src_port, dst_node, dst_port);
                    } else {
                        error_callback(i, "Expected two parts seperated by single > character");
                        return false;
                    }
                }
            }
        }

        return true;
    }

    Graph.prototype.getNodes = function() {
        return this._nodes;
    }

    Graph.prototype.getConnections = function() {
        return this._connections;
    }

    /**
     * Generate ELKjs JSON for this graph.
     */
    Graph.prototype.elkJson = function() {
        var json = {
            id: "root",
            properties: {'algorithm': 'layered'},
            children: [],
            edges: []
        }
        
        // Generate nodes with ports
        for (var node_id in this._nodes) {
            var node = this._nodes[node_id];
            var child = {};

            var nInputs = 0;
            var nOutputs = 0;
            for (var p in node['ports']) {
                if (node['ports'][p].type == 'input') {
                    nInputs += 1;
                } else {
                    nOutputs += 1;
                }
            }

            var nPorts = Math.max(nInputs, nOutputs);

            child['id'] = node_id;
            child['type'] = node.type;
            child['label'] = node.label;
            child['width'] = 40 + 6*node.label.length;
            child['height'] = 30 + nPorts * 12;
            if (node.type == 'terminal' || node.type == 'dangling') {
                child['height'] = 20;
            }
            child['labels'] = [{'id': node_id + '_label', 'text': node['label']}];
            child['ports'] = [];
            for (var port_id in node['ports']) {
                var port = node['ports'][port_id];                
                var port_obj = {
                    id: node_id + "." + port['id'],
                    label: port['label'],
                    type: port['type'],
                    width: 5,
                    height: 5,                    
                    labels: [
                        {'id': node_id + "." + port['id'] + "_label", 'text': port_id}
                    ]
                };
                child['ports'].push(port_obj);
            }

            json['children'].push(child);
        }

        // Generate edges
        for (var i = 0; i < this._connections.length; i++) {
            var connection = this._connections[i];
            var edge = {
                id: "e" + i,
                sources: [ connection['source']['node']['id'] + "." + connection['source']['id']],
                targets: [ connection['target']['node']['id'] + "." + connection['target']['id']]
            };
            json['edges'].push(edge);
        }

        return json;
    }

    return Graph;
})();