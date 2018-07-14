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

// 获取get
// 修改post
$(document).ready(function () {
    $('#user-name').change(function(){
        $('.error-msg').hide();
    })

    $.get('/api/profile', function(e){
        if(e.errcode == 4101){
            window.location.href = '/login.html'
        }
        else{
            $('#user-avatar').attr('src', e.data.avatar);
            $('#user-name').attr('placeholder', e.data.up_name);
        }
    });

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
               if(e.errcode == 0){
                   $('.image_uploading').fadeOut();
                   $('#user-avatar').attr('src', e.data);
               }
               else if(e.errcode == 4101){
                   window.location.href = '/login.html';
               }
               else{
                   alert('头像上传失败, 请重新上传');
               }
           }
       }
       $(this).ajaxSubmit(content);
    });
    $('#form-name').submit(function(e){
        e.preventDefault();
        var data = {};
        $('#form-name').serializeArray().map(function(x){
            data[x.name] = x.value
        });

        $.ajax({
            url: '/api/profile/name',
            method: 'POST',
            headers: {
                'X-XSRFTOKEN': getCookie('_xsrf')
            },
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json',
            success: function(e){
                if(e.errcode == 0){
                    $('.popup_con').fadeIn('fast', function(){
                        setTimeout(function(){
                            $('.popup_con').fadeOut('fast');
                        }, 2000)
                    })
                }
                else if(e.errcode == 4003){
                    $('.error-msg').show();
                }
                else if(e.errcode == 4101){
                   window.location.href = '/login.html';
               }
            }
        })
    })
});

