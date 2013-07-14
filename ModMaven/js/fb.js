// FB.logout() with error handling and session management
fbLogout = function() {
    FB.getLoginStatus(function(response){
        console.log(response.status);
        if(response.status === "connected"){FB.logout();}
        $.get('/logout', function(){window.location.reload();});
    }, true);
};

// Function to run after FB.init completes
fbLoaded = function(){
    FB.Event.subscribe('auth.login', function(response){
        if(response.authResponse){window.location.reload();}
    });

    // Keep verifying asynchronously,
    // if user is still logged in
    var loggedInChk = function(){
        console.log("Called");
        FB.getLoginStatus(function (response) {
            if (response.status !== 'connected') {
                $.get('/logout');
                clearInterval(intervalID);
            }
            else {

            }
            console.log(response);
        }, true);
    };
    var intervalID = setInterval(loggedInChk, 10000); // Check every 10 secs

};


// Check if correct permissions granted
var permissionsOk = function(permsNeeded) {
    FB.api('/me/permissions', function(response) {
        var permsArray = response.data[0];
        var permsToPrompt = [];
        for (var i in permsNeeded) {
            if (permsArray[permsNeeded[i]] == null) {
                permsToPrompt.push(permsNeeded[i]);
            }
        }
        if (permsToPrompt.length > 0){
            FB.login(function(){}, {scope: permsToPrompt.join(',')});
        }
    });
};

var  postify = function (){
    FB.api('me/modmaven:consider', 'post', {'module' : url}, function (response) {
        console.log(response);
    });
};

