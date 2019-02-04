/**
 * Graph visualizer based on d3.js
 */
GraphRender = (function() {

    function GraphRender() {
        if (!(this instanceof GraphRender)) {
            return new GraphRender();
        }

        this._svg = null;
    }

    /**
     * Attach the visualization to a DOM element.
     * @param selector DOM element selector string, e.g. '#id'
     */
    GraphRender.prototype.attach = function(selector) {
        var self = this;
        var zoomed = function() {
            self._svg.attr("transform", d3.event.transform);
        };

        var zoom = d3.zoom()
            .scaleExtent([0.1, 1])
            .on("zoom", zoomed);

        this._svg = d3.select(selector).append("svg")
                        .attr("width", "100%")
                        .attr("height", "100%")
                        .call(zoom);

        this.clear();
    }

    /**
     * Clear the view.
     */
    GraphRender.prototype.clear = function() {
        this._svg.selectAll("*").remove()
        this._svg.append("svg:defs").append("svg:marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr('refX', 10)//so that it comes towards the center.
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .attr("fill", "blue")
        .append("svg:path")
            .attr("d", "M0,-5L10,0L0,5");
    }

    /**
     * Draw an ELKjs graph.
     * @param graph 
     */
    GraphRender.prototype.draw = function(graph) {
        var nodes = graph.children;
        for (var i = 0; i < nodes.length; i++) {
            this.drawNode(nodes[i]);
        }

        var edges = graph.edges;
        for (var i = 0; i < edges.length; i++) {
            this.drawEdge(edges[i]);
        }
    }

    /**
     * Draw a single node with its ports.
     * @param node 
     */
    GraphRender.prototype.drawNode = function(node) {
        var group = this._svg.append("g")
                        .attr("transform", "translate(" + node.x + "," + node.y + ")");

        var label = node.label;
        var fill_color = "#DDEEFF";
        if (node.type == "terminal") {
            fill_color = "#EEFFDD";
        } else if (node.type == "dangling") {
            fill_color = "#FFDDEE";
        }

        var shape = group.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", node.width)
            .attr("height", node.height)
            .attr("rx", 6).attr("ry", 6)
            .attr("fill", fill_color)
            .attr("stroke", "#2378AE")
            .attr("stroke-width", 1.0);
        
        var label = group.append("text")
            .text(label)
            .attr("dx", node.width/2)
            .attr("dy", node.height/2)
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "central")
            .attr("font-family", "sans-serif")
            .attr("font-size", "12px")
            .attr("fill", "black");
        
        // Drawing ports
        for (var i = 0; i < node.ports.length; i++) {
            var port = node.ports[i];
            var port_shape = group.append("rect")
                .attr("width", port.width)
                .attr("height", port.height)
                .attr("x", port.x)
                .attr("y", port.y);

            if (node.type == 'node') {
                var valign = "text-before-edge";
                var dx = port.x;
                var dy = port.y;
                var color = "#FF0000";
                if (port['type'] == 'input') {
                    valign = 'auto';
                    dy -= 2;
                    color = "#FF33FF";
                } else {
                    dy += 2;
                    dx += 5;
                }  
                var port_label = group.append("text")
                    .text(port.label)
                    .attr("dx", dx)
                    .attr("dy", dy)
                    .attr("text-anchor", "middle")
                    .attr("alignment-baseline", valign)
                    .attr("font-family", "Verdana")
                    .attr("font-size", "9px")
                    .attr("fill", color);
            }
        }

    }

    /**
     * Draw a graph edge (connection).
     * @param edge 
     */
    GraphRender.prototype.drawEdge = function(edge) {
        var sections = edge['sections'];
        for (var i = 0; i < sections.length; i++) {
            var section = sections[i];
            this.drawSection(section);
        }
    }

    GraphRender.prototype.drawSection = function(section) {
        var lineData = []
        lineData.push(section.startPoint);
        if ('bendPoints' in section) {
            var bp = section.bendPoints;
            for (var i = 0; i < bp.length; i++) {
                lineData.push(bp[i]);
            }
        }
        lineData.push(section.endPoint);

        var lineFunc = d3.line()
            .x(function(d) { return d.x; })
            .y(function(d) { return d.y; })
            .curve(d3.curveLinear);
        
        var line = this._svg.append("path")
            .attr("d", lineFunc(lineData))
            .attr("stroke", "blue")
            .attr("stroke-width", 1)
            .attr("fill", "none")
            .attr("marker-end", "url(#arrow)");       
    }

    return GraphRender;

})();
