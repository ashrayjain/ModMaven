function drawTree(modName, data){
    d3.selectAll("svg")
        .remove();
    console.log($('#Tree').parent().width());
    var canvas = d3.select('#Tree')
        .append("svg")
        .attr("width", $('#Tree').parent().width())
        .attr("height", 1000)
        .append("g")
        .attr("transform", "translate(50,50");

    var borderRect = canvas.append("rect")
        .attr("width", $('#Tree').parent().width())
        .attr("height", 1000)
        .attr("stroke", "black")
        .attr("stroke-width", 2.5)
        .attr("fill", "grey")
        .attr("opacity", 0.65);

    var tree = d3.layout.tree()
        .size([$('#Tree').parent().width(), 750]);

    //var id="{{modName}}"
    //tree.children(function(d) { console.log(d[id].prereqs); return d[id].prereqs;})
    var nodes = tree.nodes(data);
    var links = tree.links(nodes);

    var node = canvas.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + (d.y + 50) + ")";
        });

    var diagonal = d3.svg.diagonal()
        .projection(function (d) {
            return [d.x, d.y + 50];
        });
    var x, y;
    canvas.selectAll(".link")
        .data(links)
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "black")
        .attr("opacity", 0)
        .attr("d", diagonal);

    var backButton = canvas.append("circle")
        .attr("r", 25)
        .attr("cx", 50)
        .attr("cy", 50)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 1.5);

    backButton.append("text")
        .text(function (d) {
            return "Back";
        })
        .style("fill", "black")
        .attr("text-anchor", "middle")
        .attr("class", "lead");

    var rectangles = node.append("rect")
        .attr("width", 0)
        .attr("height", 0)
        .attr("x", -50)
        .attr("y", -35)
        .attr("rx", 20)
        .attr("ry", 20)
        .attr("stroke", "black")
        .attr("stroke-width", 1.5)
        .attr("opacity", 1)
        .attr("nodeValue", function (d) {
            return d.name;
        })
        .attr("fill", "steelblue");

    node.append("text")
        .text(function (d) {
            return d.name;
        })
        .style("fill", "none")
        .style("opacity", 0)
        .attr("text-anchor", "middle")
        .attr("text-decoration", "underline")
        .attr("class", "lead");

    node.selectAll("rect")
        .transition()
        .duration(2000)
        .attr("width", 100)
        .attr("height", 70)
        .ease("elastic");

    node.selectAll("text")
        .transition()
        .delay(2000)
        .duration(2000)
        .style("fill", "black")
        .style("opacity", 1);

    canvas.selectAll("path")
        .transition()
        .delay(2000)
        .duration(1500)
        .attr("opacity", 1);

    rectangles.on("mouseout", function () {
        node.selectAll("rect")
            .transition()
            .attr("fill", "steelblue")
            .attr("height", 70)
            .attr("y", -35)
            .attr("x", -50)
            .attr("width", 100)
            .attr("opacity", 1);
    });
    rectangles.on("mouseover", function (d, i) {
        d3.select(this)
            .transition()
            .attr("fill", "green")
            .attr("height", 100)
            .attr("y", -50)
            .attr("x", -75)
            .attr("width", 150)
            .attr("opacity", 0.3);

        rectangles.on("click", function(d, i){
            var currNode = this.parentNode;
            var currMod = d3.select(currNode).text();

            $.getJSON('/getmod?modName=' + currMod, function (data) {

                var modalLabel = $("#myModalLabel");
                modalLabel.text(data['label']);
                modalLabel.parent().attr('href', '/modpage?modName='+currMod);

                $(".modal-body p")
                    .text(data['description']);
                $('#myModal').modal('show');
            });
        });
    });
    console.log(rectangles);
}
