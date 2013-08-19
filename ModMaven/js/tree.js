var interact,
    SVGWidth,
    SVGHeight = 550;

function zoomIn(){
    if (interact.scale() < 2.6 ){
        var translation = interact.translate();
        translation = [
            (SVGWidth) / 2 + translation[0],
            75 + translation[1]
        ];
        var interval = 0.05;
        d3.select("#drawarea")
            .attr("transform", "translate(" + translation + ")" +
                " scale(" + (interact.scale()+interval) + ")");
        interact.scale(interact.scale()+interval);
    }
}
function zoomOut(){
    if (interact.scale() > 0.3) {
        var translation = interact.translate();
        translation = [
            (SVGWidth) / 2 + translation[0],
            75 + translation[1]
        ];
        var interval = 0.05;
        d3.select("#drawarea")
            .attr("transform", "translate(" + translation + ")" +
                " scale(" + (interact.scale()-interval) + ")");
        interact.scale(interact.scale()-interval);
    }

}
function drawTree(data, toggle) {

    function getWidth(toggle){
        if (toggle === true) return 0;
        else return 60;
    }

    $("#zoom-btns").css("display", "");
    $("#legend").css("display", "");
    var btn = null,
        delay = null;
    $("#zoom-out").mousedown(function(){
        zoomOut();
        delay = setTimeout(function(){
            btn = setInterval(zoomOut, 50);
        }, 500);
    });
    $("#zoom-out").mouseup(function () {
        if(btn)
            clearInterval(btn);
        if (delay)
            clearTimeout(delay);
    });
    $("#zoom-in").mousedown(function () {
        zoomIn();
        delay = setTimeout(function () {
            btn = setInterval(zoomIn, 50);
        }, 500);
    });
    $("#zoom-in").mouseup(function () {
        if (btn)
            clearInterval(btn);
        if(delay)
            clearTimeout(delay);
    });
    SVGWidth = $("#Tree").width() - getWidth(toggle);
    d3.selectAll("svg")
        .remove();

    var canvas = d3.select('#Tree')
            .append("svg")
            .attr("id", "svg")
            .attr("width", SVGWidth)
            .attr("height", SVGHeight)
            .attr("style", "cursor: move; z-index: -999;"),
        border = canvas.append("rect")
            .attr("width", SVGWidth)
            .attr("height", SVGHeight)
            .attr("stroke", "black")
            .attr("stroke-width", 5)
            .attr("fill", "none");
    interact = d3.behavior.zoom()
        .scaleExtent([0.4, 2.6])
        .on("zoom", zoom);

    canvas = canvas.append("g")
        .attr("id", "drawarea");

    d3.select("svg").call(interact);

    function zoom() {
        var scale = d3.event.scale,
            translation = d3.event.translate;
        translation = [
            (SVGWidth) / 2 + translation[0],
            75 + translation[1]
        ];
        d3.select("#drawarea")
            .attr("transform", "translate(" + translation + ")" +
                " scale(" + scale + ")");
    }

    var aspect = $("#svg").width() / $("#svg").height();
    $(window).on("resize",function () {
        SVGWidth = $('#Tree').parent().width() - getWidth(toggle);
        d3.select("#svg")
            .attr("width", SVGWidth);
        border.attr("width", SVGWidth);
        translation = [(SVGWidth)/2, 75]
        interact.translate([0, 0]);
        d3.select("#drawarea")
            .transition()
            .delay(1)
            .attr("transform", "translate(" + translation + ")" +
                " scale("+interact.scale()+")");

    }).trigger("resize");


    var tree = d3.layout.tree()
        .nodeSize([130,130]);

    var nodes = tree.nodes(data);
    var links = tree.links(nodes);

    var node = canvas.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

    var diagonal = d3.svg.diagonal()
        .projection(function (d) {
            return [d.x, d.y];
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
        .attr("x", function (d) {
            if (d.name == 'or' || d.name == 'and') {
                return -25;
            }
            else
                return -50;
        })
        .attr("y", function (d) {
            if (d.name == 'or' || d.name == 'and') {
                return -17.5;
            }
            else
                return -35;
        })
        .attr("rx", 20)
        .attr("ry", 20)
        .attr("stroke", "black")
        .attr("stroke-width", 1.5)
        .attr("opacity", function (d) {
            if (d.name == 'or' || d.name == 'and') {
                return 0;
            }
            else
                return 1;
        })
        .attr("nodeValue", function (d) {
            return d.name;
        })
        .attr("fill", function (d) {
            if (d['done'])
                return "red";
            else if (d['prec'])
                return "yellow";
            else
                return "steelblue";
        })
        .attr("style", function (d) {
            if (d.name == 'or' || d.name == 'and')
                return "cursor:default"
        });

    var labels = node.append("text")
        .text(function (d) {
            return d.name;
        })
        .style("fill", "none")
        .style("opacity", 0)
        .attr("dy", function (d) {
            if (d.name == 'or' || d.name == 'and')
                return "10";
            return "";
        })
        .attr("text-anchor", "middle")
        .attr("text-decoration", function (d) {
            if (d.name == 'or' || d.name == 'and')
                return ""
            return "underline";
        })
        .attr("class", "lead");

    node.selectAll("rect")
        .transition()
        .duration(2000)
        .attr("width", function (d) {
            if (d.name == 'or' || d.name == 'and')
                return 50;
            else
                return 100;
        })
        .attr("height", function (d) {
            if (d.name == 'or' || d.name == 'and')
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
        .each("end", function () {
            node.on("mouseout", function () {
                node.selectAll("rect")
                    .transition()
                    .attr("fill", function (d) {
                        if (d['done'])
                            return "red";
                        else if (d['prec'])
                            return "yellow";
                        else
                            return "steelblue";
                    })
                    .attr("height", function (d) {
                        if (d.name == 'or' || d.name == 'and')
                            return 35;
                        else
                            return 70;
                    })
                    .attr("y", function (d) {
                        if (d.name == 'or' || d.name == 'and')
                            return -17.5;
                        else
                            return -35;
                    })
                    .attr("x", function (d) {
                        if (d.name == 'or' || d.name == 'and')
                            return -25;
                        else
                            return -50;
                    })
                    .attr("width", function (d) {
                        if (d.name == 'or' || d.name == 'and')
                            return 50;
                        else
                            return 100;
                    })
                    .attr("opacity", function (d) {
                        if (d.name == 'and' || d.name == 'or')
                            return 0;
                        else
                            return 1;
                    });
                node.selectAll("text")
                    .transition()
                    .style("opacity", 1);
            });
            node.on("mouseover", function (d) {
                if (d.name != 'and' && d.name != 'or') {
                    node.selectAll("rect")
                        .transition()
                        .attr("fill", function (d) {
                            if (d['done'])
                                return "red";
                            else if (d['prec'])
                                return "yellow";
                            else
                                return "steelblue";
                        })
                        .attr("height", function (d) {
                            if (d.name == 'and' || d.name == 'or')
                                return 35;
                            else
                                return 70;
                        })
                        .attr("y", function (d) {
                            if (d.name == 'and' || d.name == 'or')
                                return -17.5;
                            else
                                return -35;
                        })
                        .attr("x", function (d) {
                            if (d.name == 'and' || d.name == 'or')
                                return -25;
                            else
                                return -50;
                        })
                        .attr("width", function (d) {
                            if (d.name == 'and' || d.name == 'or')
                                return 50;
                            else
                                return 100;
                        })
                        .attr("opacity", function (d) {
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

                    node.on("click", function (d) {
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
                                    modalLabel.text(currMod + " - " + data["ModuleTitle"]);
                                    modalLabel.parent().attr('href', '/modpage?modName=' + currMod);
                                    footerLink.attr('href', '/modpage?modName=' + currMod);

                                    var modalBody = null;
                                    if (data["ModuleDescription"] !== undefined) {
                                        modalBody = data["ModuleDescription"];
                                    }
                                    else {
                                        modalBody = "Not Available";
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
                                setTimeout(function () {
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
