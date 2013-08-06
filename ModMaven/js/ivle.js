function closePopup(popup) {
    if (popup.location.href !== undefined && popup.location.href.indexOf("http://ash.pagekite.me/ivle") === 0){
        clearInterval(popupClose);
        //console.log("Sent");
        $.post('/ivle', {token: (popup.location.href.split("token=")[1]).split("&")[0]});
        popup.close();
        $("#ivle-alert").alert('close');
    }
}
