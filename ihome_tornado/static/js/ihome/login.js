function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $('#mobile').change(function(){
        $("#mobile-err").hide();
    })
    $('#password').change(function(){
        $('#password-err').hide();
    });
    $('.form-login').submit(function(event) {
        /* Act on the event */
        event.preventDefault();
        var mobile = $('#mobile').val();
        var password = $('#password').val();
        if(!mobile){
            $('#mobile-err span').html('请输入手机号')
            $('#mobile-err').show()
            return;
        }
        if(!password){
            $('#password-err span').html('请输入密码')
            $('#password-err').show()
            return;
        }
        var data = {};
        $('.form-login').serializeArray().map(function(x){
            data[x.name] = x.value;
        });

        $.ajax({
            url: '/api/login',
            method: 'POST',
            headers: {
                'X-XSRFTOKEN': getCookie('_xsrf'),
            },
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            success: function(e){
                if(e.errcode == 0){
                    window.location.href='/';
                }
                else if(e.errcode == 4106){
                    $('#password-err span').html('密码错误');
                    $('#password-err').show();
                }
                else if(e.errcode == 4104){
                    $('#mobile-err span').html('该用户不存在');
                    $('#mobile-err').show();
                }

            }
        })
    });
})
