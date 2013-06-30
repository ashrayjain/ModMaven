$(document).ready(function(){
    $('a[data-toggle="pill"]').on('shown', function (e) {
        if(e.target.innerText === "Tree" && e.relatedTarget.innerText !== "Tree")
        {

            d3.selectAll("svg")
                .remove();
            var canvas = d3.select('.TreeSpace')
                .append("svg")
                .attr("width", 1000)//document.getElementsByTagName('body')[0].clientWidth/1.5)
                .attr("height", 1500)
                .append("g")
                .attr("transform", "translate(50,50");

            var borderRect = canvas.append("rect")
                .attr("width", 1000)//document.getElementsByTagName('body')[0].clientWidth/1.5)
                .attr("height",1500)
                .attr("stroke","black")
                .attr("stroke-width", 2.5)
                .attr("fill","grey")
                .attr("opacity", 0.65);

            var tree = d3.layout.tree()
                .size([1000,750]);

            d3.json("http://localhost:8080/data/testInfo.json", function (error,jsonData) {
                
                //console.log(treeData);
                var nodes = tree.nodes(jsonData);
                var links = tree.links(nodes);
                //console.log(jsonData[currMod]);
                var node = canvas.selectAll(".node")
                    .data(nodes)
                    .enter()
                    .append("g")
                    .attr("class","node")
                    .attr("transform", function (d) { return "translate(" + d.x + "," + (d.y + 50) + ")"; })

                var diagonal = d3.svg.diagonal()
                    .projection(function(d) { return [d.x, d.y+50]; });

                canvas.selectAll(".link")
                    .data(links)
                    .enter()
                    .append("path")
                    .attr("class", "link")
                    .attr("fill","none")
                    .attr("stroke", "black")
                    .attr("opacity", 0)
                    .attr("d", diagonal);

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
                    .attr("fill", "steelblue");

                node.append("text")
                    .text(function(d) { return d.name; })
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
                    .style("opacity",1);

                canvas.selectAll("path")
                    .transition()
                    .delay(2000)
                    .duration(1500)
                    .attr("opacity",1);

                rectangles.on("mouseout", function() {
                    node.select("rect")
                        .transition()
                        .attr("fill","steelblue")
                        .attr("height",70)
                        .attr("y",-35)
                        .attr("x",-50)
                        .attr("width", 100)
                        .attr("opacity",1);
                })
                rectangles.on("mouseover", function(d,i){
                    d3.select(this)
                        .transition()
                        .attr("fill","green")
                        .attr("height", 100)
                        .attr("y", -50)
                        .attr("x",-75)
                        .attr("width",150)
                        .attr("opacity",0.3);
                })
                rectangles.on("click", function(d,i) {
                                        
                                        var currNode=this.parentNode;
                                        var currMod= d3.select(currNode).text();
                                        //console.log(currNode);
                                        d3.select(".modal-body")
                                            .select("p")
                                            .text(currMod);    
                                        $('#myModal').modal('show');
                                    })
                //console.log(rectangles);
            })
        }
    });
});
