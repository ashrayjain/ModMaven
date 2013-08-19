var friendLikers = [],
    friendCompletions = [],
    loading = $('#loading-gif'),
    statsLoadingBar = $("#stats-loading-bar"),
    permsOk,
    tokenRefreshNeeded;

// Check if correct permissions granted
function onClickShowInterest(actionID, token, fromError, logoutNeeded){
    fromError = (typeof(fromError) === 'undefined') ? false : fromError;
    logoutNeeded = (typeof(logoutNeeded) === 'undefined') ? false : logoutNeeded;
    loading.css({
        right: fromError ? '259px' : '123px',
        visibility: 'visible'
    });
    if (permsOk)
        FB.api('me/modmaven:consider','post',{module: window.location.href,access_token: token},
            function (success_response) {
                console.log(success_response);
                if (success_response.hasOwnProperty("error"))
                    intermittentError(actionID, true);
                else
                    $.post('/modtaken', {'mod': window.location.href}, function(){
                        switchInterest(success_response.id);
                        if(logoutNeeded)
                            $.post('/logout');
                    });
            }
        );
    else
        FB.login(function (response) {
            FB.api(
                '/me/permissions',
                function (rechk_response) {
                    var permsArray = rechk_response.data[0],
                        permsToPrompt = [],
                        permsNeeded = ['publish_actions'];
                    for (var i in permsNeeded)
                        if (permsArray[permsNeeded[i]] == null)
                            permsToPrompt.push(permsNeeded[i]);
                    permsOk = permsToPrompt.length <= 0;
                    if (permsOk)
                        $.post('/logout', function () {
                            FB.api('me/modmaven:consider', 'post', {module: window.location.href, access_token: token},
                                function (success_response) {
                                    if(success_response.hasOwnProperty("error"))
                                        intermittentError(actionID, true);
                                    else
                                        $.post('/modtaken', {'mod': window.location.href}, function () {
                                            switchInterest(success_response.id);
                                        });
                                }
                            );
                        });
                    else
                        intermittentError(actionID, true);
                });
        }, {scope: 'publish_actions'});
}

function onClickRevokeInterest(actionID, token, fromError, logoutNeeded){
    fromError =  (typeof(fromError) === 'undefined')?false:fromError;
    logoutNeeded = (typeof(logoutNeeded) === 'undefined') ? false : logoutNeeded;
    loading.css({
        right: fromError?'259px':'132px',
        visibility: 'visible'
    });
    if (permsOk)
        FB.api('/' + actionID,'delete',{access_token: token},
            function (del_response) {
                if(del_response.hasOwnProperty('error'))
                    intermittentError(actionID, false);
                else
                    $.ajax({
                        url: '/modtaken?mod='+window.location.href,
                        type: 'DELETE',
                        success: function () {
                            switchInterest(null);
                            if(logoutNeeded)
                                $.post('/logout');
                        }
                    });
            }
        );
    else
        FB.login(function (response) {
            FB.api(
                '/me/permissions',
                function (rechk_response) {
                    var permsArray = rechk_response.data[0],
                        permsToPrompt = [],
                        permsNeeded = ['publish_actions'];
                    for (var i in permsNeeded)
                        if (permsArray[permsNeeded[i]] == null)
                            permsToPrompt.push(permsNeeded[i]);
                    permsOk = permsToPrompt.length <= 0;
                    if(permsOk)
                        FB.api('/' + actionID, 'delete', {access_token: response.authResponse.accessToken},
                            function (del_response) {
                                if(del_response.hasOwnProperty("error"))
                                    intermittentError(actionID, false);
                                else
                                    $.ajax({
                                        url: '/modtaken?mod=' + window.location.href,
                                        type: 'DELETE',
                                        success: function () {switchInterest(null);}
                                    });
                            }
                        );
                    else
                        intermittentError(actionID, false);
                });
        }, {scope: 'publish_actions'});
}

function intermittentError(actionID, prevActionShow){
    loading.css('visibility', 'hidden');
    $('#interest')
        .removeClass("btn-success btn-danger")
        .addClass("btn-warning")
        .html("Oops..Something's not right! Click to fix")
        .unbind('click')
        .click(function(){
            loading.css({
                right: '259px',
                visibility: 'visible'
            });
            FB.login(function (response) {
                FB.api(
                    '/me/permissions',
                    function (rechk_response) {
                        var permsArray = rechk_response.data[0],
                            permsToPrompt = [],
                            permsNeeded = ['publish_actions'];
                        for (var i in permsNeeded)
                            if (permsArray[permsNeeded[i]] == null)
                                permsToPrompt.push(permsNeeded[i]);
                        permsOk = permsToPrompt.length <= 0;
                        loading.css('visibility', 'hidden');
                        if (permsOk)
                            prevActionShow?
                                onClickShowInterest(actionID, response.authResponse.accessToken, true):
                                onClickRevokeInterest(actionID, response.authResponse.accessToken, true);
                    });
            }, {scope: 'publish_actions'});
        });
}
function switchInterest(actionID, token){
    var interestButton = $('#interest');
    loading.css('visibility', 'hidden');
    if(actionID!==null){
        interestButton
            .removeClass('btn-success btn-warning')
            .addClass('btn-danger')
            .html("Revoke Interest")
            .unbind('click')
            .click(function(){
                onClickRevokeInterest(actionID, token);
            });
    }
    else{
        interestButton
            .removeClass('btn-danger btn-warning')
            .addClass('btn-success')
            .html("Show Interest")
            .unbind('click')
            .click(function(){
                onClickShowInterest(actionID, token);
            });
    }
}

function initializeInterestButton(token) {
    FB.api(
        'me/modmaven:consider',
        'get',
        {
            access_token: token,
            fields: 'data'
        },
        function (action_response){
            var actionID = null;
            if (action_response.data.length != 0) {
                for (var i = 0, len = action_response.data.length; i < len; ++i) {
                    var data = action_response.data[i];
                    if (data.data.module.url === window.location.href) {
                        actionID = data.id;
                        break;
                    }
                }
            }
            loading.css('visibility', 'hidden');
            $('#interest')
                .css({visibility: 'visible'});
            switchInterest(actionID, token);
        }
    );
}

function getStats(token, modName){
    FB.api(
        '/me/friends',
        {
            access_token: token,
            fields: "id,name,link"
        },
        function (response) {
            $.getJSON('/getusers?modName='+modName, function (data) {
                getFriendLikers(response, data);
                $("#total-users").html("<h5>" + Object.keys(data).length + " User(s)</h5>");
            });
            $.get('/chkIVLE', function (chk) {
                if (chk === "0")
                    $("#frnds-completed").html("<tr><td>Please <a href='#' onclick='ivleVerify(); return false;'>Verify IVLE</a> for this information.</td></tr>");
                else
                    $.getJSON('/getusercompletions?modName='+modName, function (data) {
                        getFriendCompletions(response, data);
                    });
                statsLoadingBar.css("display", "none");
                $('#stats-content').css("display", "");
            });
        });
}

function getFriendLikers(response, data){
    for (var i = 0, len = response.data.length; i < len; i++)
        if (data.hasOwnProperty(response.data[i].id))
            friendLikers.push(response.data[i]);
    var body = $("#frnds-considered");
    if (friendLikers.length === 0)
        body.html('<div class="row-fluid"><div class="span12">No Friends have considered this module.</div></div>')
    else {
        var user = "<div class='span3' style='margin: 7px;'><table><tr><td style = 'border: none'><a href={} target='_blank' style='outline:none'><img src='https://graph.facebook.com/{}/picture'/></a></td><td style = 'border: none; vertical-align: middle; font-size: 19px;'>{}</td></tr></table></div>",
            count = 0,
            html = "";
        for (var i = 0; i < friendLikers.length; i++, count++) {
            var friend = friendLikers[i];
            if (count % 4 === 0)
                html += "<div class='row-fluid'>";
            html += user.format(friend['link'], friend['id'], friend['name']);
            if (count % 4 === 3)
                html += "</div>";
        }
        body.html(html);
    }
}

function getFriendCompletions(response, data){
    //console.log(data);
    //console.log(response);
    for (var i = 0, len = response.data.length; i < len; i++)
        if (data.hasOwnProperty(response.data[i].id))
            friendCompletions.push(response.data[i]);
    //console.log(friendCompletions);
    var body = $("#frnds-completed");
    if (friendCompletions.length === 0)
        body.html('<div class="row-fluid"><div class="span12">No Friends have completed this module.</div></div>')
    else {
        var user = "<div class='span3' style='margin: 7px;'><table><tr><td style = 'border: none'><a href={} target='_blank' style='outline:none'><img src='https://graph.facebook.com/{}/picture'/></a></td><td style = 'border: none; vertical-align: middle; font-size: 19px;'>{}</td></tr></table></div>",
            count = 0,
            html = "";
        for (var i = 0; i < friendCompletions.length; i++, count++) {
            var friend = friendCompletions[i];
            if (count % 4 === 0)
                html += "<div class='row-fluid'>";
            html += user.format(friend['link'], friend['id'], friend['name']);
            if (count % 4 === 3)
                html += "</div>";
        }
        body.html(html);
    }
}
