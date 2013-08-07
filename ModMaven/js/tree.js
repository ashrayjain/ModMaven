function drawTree(data){

    d3.selectAll("svg")
        .remove();

    // compute the new height
    var noLevels = 1;

    var childCount = function (level, n) {
        if((level + 1) > noLevels){
            noLevels = level + 1;
        }
        if (n.children && n.children.length > 0) {
            n.children.forEach(function (d) {
                childCount(level + 1, d);
            });
        }
    };
    childCount(0, data);
    var newHeight = noLevels * 104 + (noLevels-1)*10;

    var parentWidth = $('#Tree').parent().width();
    var canvas = d3.select('#Tree')
        .append("svg")
        .attr("id", "svg")
        .attr("width", parentWidth)
        .attr("height", newHeight)
        .attr("viewBox", "0 0 "+parentWidth+" "+newHeight)
        .attr("preserveAspectRatio", "xMidYMid")
        .append("g");

    var aspect = $("#svg").width() / $("#svg").height();

    $(window).on("resize",function () {
        parentWidth = $('#Tree').parent().width();
        d3.select("#svg")
            .attr("width", parentWidth)
            .attr("height", Math.round(parentWidth / aspect));
    }).trigger("resize");

    /*var borderRect = canvas.append("rect")
     .attr("width", parentWidth)
     .attr("height", 1000)
     .attr("stroke", "black")
     .attr("stroke-width", 2.5)
     .attr("fill", "grey")
     .attr("opacity", 0.65);
     */
    var tree = d3.layout.tree()
        .size([parentWidth-150, newHeight-102]);

    var nodes = tree.nodes(data);
    var links = tree.links(nodes);

    var node = canvas.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", function (d) {
            return "translate(" + (d.x+75) + "," + (d.y+51) + ")";
        });

    var diagonal = d3.svg.diagonal()
        .projection(function (d) {
            return [d.x+75, d.y+51];
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

    var rectangles = node.append("rect")
        .attr("width", 0)
        .attr("height", 0)
        .attr("x", function(d) {
            if (d.name=='or'||d.name=='and') {
                return -25;
            }
            else
                return -50;
        })
        .attr("y", function(d) {
            if (d.name=='or'||d.name=='and') {
                return -17.5;
            }
            else
                return -35;
        })
        .attr("rx", 20)
        .attr("ry", 20)
        .attr("stroke", "black")
        .attr("stroke-width", 1.5)
        .attr("opacity", function(d) {
            if (d.name=='or'||d.name=='and') {
                return 0;
            }
            else
                return 1;
        })
        .attr("nodeValue", function (d) {
            return d.name;
        })
        .attr("fill", function(d){
            if(d['done']){
                return "red";
            }
            else if (d.name=='or' || d.name=='and') {
                return "white";
            }
            else{
                return "steelblue";
            }
        })
        .attr("style", function(d){
            if (d.name == 'or' || d.name == 'and')
                return "cursor:default"
        });

    var labels = node.append("text")
        .text(function (d) {
            return d.name;
        })
        .style("fill", "none")
        .style("opacity", 0)
        .attr("dy", function(d){
            if (d.name == 'or' || d.name == 'and')
                return "10";
            return "";
        })
        .attr("text-anchor", "middle")
        .attr("text-decoration", function(d) {
            if (d.name == 'or' || d.name == 'and')
                return ""
            return "underline";
        })
        .attr("class", "lead");

    node.selectAll("rect")
        .transition()
        .duration(2000)
        .attr("width", function(d) {
            if (d.name=='or'||d.name=='and')
                return 50;
            else
                return 100;
        })
        .attr("height", function(d) {
            if (d.name=='or'||d.name=='and')
                return 35;
            else
                return 70;
        })
        .ease("elastic");

    canvas.selectAll("path")
        .transition()
        .delay(1000)
        .duration(1000)
        .attr("opacity", 1);

    node.selectAll("text")
        .transition()
        .delay(1000)
        .duration(1000)
        .style("fill", "black")
        .style("opacity", 1)
        .attr("style", function (d) {
            if (d.name == 'or' || d.name == 'and')
                return "cursor:default; font-size: 50px;"
        })
        .each("end",function(){
            node.on("mouseout", function () {
                node.selectAll("rect")
                    .transition()
                    .attr("fill", function(d){
                        if(d['done'])
                            return "red";
                        else if(d.name=='and' || d.name=='or')
                            return "white";
                        else
                            return "steelblue";
                    })
                    .attr("height", function(d) {
                        if (d.name=='or'||d.name=='and')
                            return 35;
                        else
                            return 70;
                    })
                    .attr("y", function(d) {
                        if (d.name=='or'||d.name=='and')
                            return -17.5;
                        else
                            return -35;
                    })
                    .attr("x", function(d) {
                        if (d.name=='or'||d.name=='and')
                            return -25;
                        else
                            return -50;
                    })
                    .attr("width", function(d) {
                        if (d.name=='or'||d.name=='and')
                            return 50;
                        else
                            return 100;
                    })
                    .attr("opacity", function (d) {
                        if(d.name=='and' || d.name=='or')
                            return 0;
                        else
                            return 1;
                    });
                node.selectAll("text")
                    .transition()
                    .style("opacity", 1);
            });
            node.on("mouseover", function (d, i){
                if(d.name!='and' && d.name!='or') {
                    node.selectAll("rect")
                        .transition()
                        .attr("fill", function(d){
                            if(d['done']){
                                return "red";
                            }
                            else if(d.name=='and' || d.name=='or') {
                                return "white";
                            }
                            else{
                                return "steelblue";
                            }
                        })
                        .attr("height", function (d){
                            if(d.name=='and' || d.name=='or')
                                return 35;
                            else
                                return 70;
                        })
                        .attr("y", function (d){
                            if(d.name=='and' || d.name=='or')
                                return -17.5;
                            else
                                return -35;
                        })
                        .attr("x", function (d){
                            if(d.name=='and' || d.name=='or')
                                return -25;
                            else
                                return -50;
                        })
                        .attr("width", function (d){
                            if(d.name=='and' || d.name=='or')
                                return 50;
                            else
                                return 100;
                        })
                        .attr("opacity", function(d){
                            if (d.name == 'and' || d.name == 'or')
                                return 0;
                            else
                                return 0.3;
                        });
                    node.selectAll("text")
                        .transition()
                        .style("opacity", 0.3);
                    d3.select(this)
                        .select("text")
                        .transition()
                        .style("opacity", 1);

                    d3.select(this)
                        .select("rect")
                        .transition()
                        .attr("fill", "green")
                        .attr("height", 100)
                        .attr("y", -50)
                        .attr("x", -75)
                        .attr("width", 150)
                        .attr("opacity", 0.8);


                    node.on("click", function (d, i) {
                        if (d.name != 'and' && d.name != 'or') {
                            var modaldivs = $('.modal-header, .modal-body, .modal-footer');
                            var bar = $('#loading-bar');
                            modaldivs.css('display', 'none');
                            bar.css('display', '');
                            var modal = $('#myModal');
                            modal.css({
                                'background': 'transparent none',
                                'box-shadow': 'none',
                                'border': 'none',
                                'top': '40%'
                            })
                                .modal('show');

                            var currMod = d3.select(this).text();
                            $.getJSON('/getmod?modName=' + currMod, function (data) {
                                var modalLabel = $("#myModalLabel");
                                var footerLink = $("#knowmore");
                                if ($.isEmptyObject(data)) {

                                    modalLabel.text(currMod);
                                    modalLabel.parent().attr('href', '#');
                                    footerLink.attr('href', '#');

                                    $(".modal-body p")
                                        .text("No Information Available");
                                }
                                else {
                                    modalLabel.text(currMod+" - "+data["ModuleTitle"]);
                                    modalLabel.parent().attr('href', '/modpage?modName=' + currMod);
                                    footerLink.attr('href', '/modpage?modName=' + currMod);

                                    if (data["ModuleDescription"] !== undefined) {
                                        var modalBody = data["ModuleDescription"];
                                    }
                                    else {
                                        var modalBody = "Not Available";
                                    }
                                    if (typeof data['Prerequisite'] == "string" && data['Prerequisite'].length > 9) {
                                        modalBody += '<br><br><b>Prerequisite: </b><br>' + data['Prerequisite'];
                                    }
                                    $(".modal-body p")
                                        .html(modalBody);
                                }
                                modal
                                    .addClass('notransition')
                                    .css({
                                        'top': '-25%',
                                        'background': '',
                                        'box-shadow': '',
                                        'border': '',
                                        'opacity': '0'
                                    });
                                modaldivs.css('display', '');
                                bar.css('display', 'none');
                                setTimeout(function(){
                                    modal
                                        .removeClass('notransition')
                                        .css({
                                            'top': '10%',
                                            'opacity': '1'
                                        });
                                }, 10);
                            });
                        }
                    });
                }
            });
        });
}
