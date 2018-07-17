function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.get("/api/house/area", function (data) {
        if ("0" == data.errcode) {
            console.log(data);
            $('.form-control').html(template('area-tmpl', {areas: data.data}))
        }
        else if('4101' == data.errcode){
            window.location.href = '/login.html';
        }
    })
    $('#form-house-info').submit(function(e){
        e.preventDefault();

    })
})