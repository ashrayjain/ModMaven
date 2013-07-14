function closePopup(popup) {
    if (popup.location.href !== undefined && popup.location.href.indexOf("http://localhost:8080/ivle") === 0){
        var urlParams;
        var match,
            pl = /\+/g,  // Regex for replacing addition symbol with a space
            search = /([^&=]+)=?([^&]*)/g,
            decode = function (s) {
                return decodeURIComponent(s.replace(pl, " "));
            },
            query = popup.location.search.substring(1);

        urlParams = {};
        while (match = search.exec(query))
            urlParams[decode(match[1])] = decode(match[2]);
        clearInterval(popupClose);
        console.log("Sent");
        $.post('/ivle', urlParams);
        popup.close();
    }
}
