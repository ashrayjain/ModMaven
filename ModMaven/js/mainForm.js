$('#main-form').attr("onsubmit", "return processForm();");
var  prevMod = null;
processForm = function(){
    var modName = $("#modName").val();
    if(prevMod !== null && modName === prevMod){
        return false;
    }
    prevMod = modName;
    $('#loading-gif').css("visibility", "visible");
    $.getJSON('/gettree?modName=' + modName, function (data) {
        if ($.isEmptyObject(data)){
            $("#errormessage").text("The Module You Requested Was Not Found");
        }
        else{
            $("#errormessage").text("");
            drawTree(data, false);
        }
        $('#loading-gif').css("visibility", "hidden");
    });
    return false;
};
