function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $.get()
    $('#form-avatar').submit(function(e){
       e.preventDefault();
       $('.image_uploading').fadeIn();
       var content = {
           url: '/api/profile/avatar',
           method: 'POST',
           headers: {
               'X-XSRFTOKEN': getCookie('_xsrf')
           },
           dataType: 'json',
           success: function(e){
               if(e.errcode == '0'){
                   $('.image_uploading').fadeOut();
                   $('#user-avatar').attr('src', e.data);
               }
               else if(e.errcode == '4101'){
                   window.location.href = '/login.html';
               }
               else{
                   alert('头像上传失败, 请重新上传');
               }
           }
       }
    });

})

