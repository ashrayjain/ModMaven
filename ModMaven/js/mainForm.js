$('#main-form').attr("onsubmit", "return processForm();");

processForm = function(){
    var modName = $("#modName").val();
    $('#loading-gif').css("visibility", "visible");
    $.getJSON('/gettree?modName=' + modName, function (data) {
        if ($.isEmptyObject(data)){
            $("#errormessage").text("The Module You Requested Was Not Found");
        }
        else{
            $("#errormessage").text("");
            drawTree(data);
        }
        $('#loading-gif').css("visibility", "hidden");
    });
    return false;
};
