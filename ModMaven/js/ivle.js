function closePopup(popup) {
    if (popup.location.href !== undefined && popup.location.href.indexOf("http://nusmodmaven.appspot.com/ivle") === 0){
        clearInterval(popupClose);
        $.post('/ivle', {token: (popup.location.href.split("token=")[1]).split("&")[0]}, function(data) {
            popup.close();
            $("#ivle-alert").alert('close');
        });
    }
}
