var friendLikers = new Array();
var statsLoadingBar = $("#stats-loading-bar");
var loading = $('#loading-gif');

// Check if correct permissions granted
function permissionsOk(permsNeeded, token, actionID, callback) {
    FB.api(
        '/me/permissions',
        {
            access_token: token
        },
        function(response) {
            var permsArray = response.data[0];
            var permsToPrompt = [];
            for (var i in permsNeeded) {
                if (permsArray[permsNeeded[i]] == null) {
                    permsToPrompt.push(permsNeeded[i]);
                }
            }
            if (permsToPrompt.length > 0){
                FB.login(function(response){
                    FB.api(
                        '/me/permissions',
                        function (rechk_response) {
                            var permsArray = rechk_response.data[0];
                            var permsToPrompt = [];
                            for (var i in permsNeeded) {
                                if (permsArray[permsNeeded[i]] == null) {
                                    permsToPrompt.push(permsNeeded[i]);
                                }
                            }
                            if (permsToPrompt.length === 0){
                                callback(actionID, response.authResponse.accessToken);
                            }
                            else{
                                loading.css('visibility', 'hidden');
                            }
                        });
                }, {scope: permsToPrompt.join(',')});
            }
        });
}

function onClickShowInterest(actionID, token){
    loading.css({
        right: '123px',
        visibility: 'visible'
    });
    FB.api(
        'me/modmaven:consider',
        'post',
        {
            module: window.location.href,
            access_token: token
        },
        function (success_response) {
            console.log(success_response);
            if (success_response.hasOwnProperty("error")) {
                $.get('/logout');
                permissionsOk(["publish_actions"], token, actionID, onClickShowInterest);
            }
            else {
                $.post('/modtaken', {'mod': window.location.href}, function(){switchInterest(success_response.id);});
            }
        }
    );
}

function onClickRevokeInterest(actionID, token){
    loading.css({
        right: '132px',
        visibility: 'visible'
    });
    FB.api(
        '/' + actionID,
        'delete',
        {
            access_token: token
        },
        function (del_response) {
            if (del_response.hasOwnProperty("error")) {
                $.get('/logout');
                permissionsOk(["publish_actions"], token, actionID, onClickRevokeInterest);
            }
            else if (del_response === true) {
                $.ajax({
                    url: '/modtaken?mod='+window.location.href,
                    type: 'DELETE',
                    success: function () {
                        switchInterest(null);
                    }
                });
            }
        }
    );
}

function switchInterest(actionID, token){
    var interestButton = $('#interest');
    loading.css('visibility', 'hidden');
    if(actionID!==null){
        interestButton
            .removeClass('btn-success')
            .addClass('btn-danger')
            .html("Revoke Interest")
            .unbind('click')
            .click(function(){
                onClickRevokeInterest(actionID, token);
            });
    }
    else{
        interestButton
            .removeClass('btn-danger')
            .addClass('btn-success')
            .html("Show Interest")
            .unbind('click')
            .click(function(){
                onClickShowInterest(actionID, token);
            });
    }
}

function initializeInterestButton(token) {
    console.log("Access Token: " + token);
    if (token === "") {
        loading.css('visibility', 'hidden');
        $('#login-required').css('display', '');
        return;
    }
    FB.api(
        'me/modmaven:consider',
        'get',
        {
            access_token: token,
            fields: 'data'
        },
        function (action_response){
            var actionID = null;
            if (action_response.hasOwnProperty("error")) {
                $.get('/logout');
                FB.login(function (response){
                    if (response.authResponse){
                        initializeInterestButton(response.authResponse.accessToken);
                    }
                    else{
                        loading.css('visibility', 'hidden');
                        $('#login-required').css('display', '');
                    }
                });
            }
            else {
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
        }
    );
}

function getFriendLikers(token, data){
    FB.api(
        '/me/friends',
        {
            access_token: token,
            fields: "id,name,link"
        },
        function(response){
            if (response.hasOwnProperty("error")) {
                $.get('/logout');
                FB.login(function (response) {
                    if (response.authResponse) {
                        getFriendLikers(response.authResponse.accessToken, data);
                    }
                    else {
                        statsLoadingBar.css('visibility', 'hidden');
                        //Show Error
                    }
                });
            }
            else{
                for (var i = 0, len = response.data.length; i < len; i++) {

                    if (data.hasOwnProperty(response.data[i].id)) {
                        friendLikers.push(response.data[i]);

                    }
                }
            }
            console.log(friendLikers);
            var firstrow = $("#firstrow");
            if (friendLikers.length === 0) {
                firstrow.html("<td>No Friends have considered this module.</td>")
            }
            else {
                var user = "<td><table><tr><td style = 'border: none'><a href={} target='_blank' style='outline:none'><img src='https://graph.facebook.com/{}/picture'/></a></td><td style = 'border: none'>{}</td></tr></table></td>"
                for (var i = 0; i < friendLikers.length; i++) {
                    var friend = friendLikers[i];
                    firstrow.html(firstrow.html() + user.format(friend['link'], friend['id'], friend['name']));
                }

            }
            $("#total-users").html("<h5>" + Object.keys(data).length + " User(s)</h5>");
            statsLoadingBar.css("display", "none");
            $('#stats-content').css("display", "");

        });
}

