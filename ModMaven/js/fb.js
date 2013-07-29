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
            console.log(response);
        }, true);
    };
    var intervalID = setInterval(loggedInChk, 10000); // Check every 10 secs

};
