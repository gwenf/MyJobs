// We used to cut and paste this function in various places. Yay modules!
function read_cookie(cookie) {
    var nameEQ = cookie + "=",
        ca = document.cookie.split(';');
    for (var i=0; i< ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// Only exporting this for now since it is what is actually needed.
export function getCsrf() {
    return read_cookie("csrftoken");
}