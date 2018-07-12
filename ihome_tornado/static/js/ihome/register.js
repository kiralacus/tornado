// 手机号输入错误是参数
var MOBILE_ERR = false;
var MOBILE_ERR_CONTENT = '';
var PICCODE_ERR = false;
var PICCODE_ERR_CONTENT = '';
var PHONECODE_ERR = false;
var PHONECODE_ERR_CONTENT = '';
var imageCodeId = "";
var PASSWORD_ERR = false;
var PASSWORD_ERR_CONTENT = '';
var PASSWORD_ERR2 = false;
var PASSWORD_ERR2_CONTEN = '';

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    var picId = generateUUID();
    $(".image-code img").attr("src", "/api/pitcode?precodeid="+imageCodeId+"&codeid="+picId);
    imageCodeId = picId;
}

// 判断输入的手机号是否正确
function mobile_check(){
    var re = /^1[3|4|5|8][0-9]\d{8}$/;
    var mobile_input = $('#mobile').val();
    // 手机号没有输入
    if(!mobile_input){
        MOBILE_ERR = true;
        MOBILE_ERR_CONTENT = '手机号不能为空';
        $('#mobile-err span').html(MOBILE_ERR_CONTENT);
        $('#mobile-err').show();
        return MOBILE_ERR;
    }
    // 手机号匹配不正确
    else if(!re.test(mobile_input)){
        MOBILE_ERR = true;
        MOBILE_ERR_CONTENT = '请输入正确的手机号';
        $('#mobile-err span').html(MOBILE_ERR_CONTENT);
        $('#mobile-err').show();
        return MOBILE_ERR;
    }
    // 手机号正确输入
    else{
        MOBILE_ERR = false;
        $('#mobile-err').hide();
        return MOBILE_ERR;
    }
}

function sendSMSCode(obj){
    var mobile = $('#mobile').val();
    var piccode = $('#imagecode').val();
    var piccode_id = imageCodeId;
    $(obj).removeAttr('onclick');
    // 判断是否输入手机号
    if(mobile_check()){
        $(obj).attr('onclick', sendSMSCode(this));
        $('.phonecode-a').attr('onclick', 'sendSMSCode(this)');
        return;
    }
    // 判断是否输入图片验证码
    if(!piccode){
        PICCODE_ERR_CONTENT = '验证码不能为空';
        $('#image-code-err span').html(PICCODE_ERR_CONTENT);
        $('#image-code-err').show();
        $('.phonecode-a').attr('onclick', 'sendSMSCode(this)');
        return;
    }

    var  param = {
        'mobile': mobile,
        'piccode': piccode,
        'piccode_id': piccode_id,
    };
    $.ajax({
        url:'/api/smscode',
        method: 'POST',
        headers: {
            'X-XSRFTOKEN': getCookie('_xsrf'),
        },
        data: JSON.stringify(param),
        contentType: 'application/json',
        dataType: 'json',
        success: function(stat){
            if(stat.errcode == 0){
                var duration = 60;
                var content = $(obj).html();
                var timeout = setInterval(function(){
                    duration = duration - 1;
                    $(obj).html(duration);

                    if(duration == 0){
                        clearInterval(timeout);
                        $(obj).html(content);
                        $(obj).attr('onclick', 'sendSMSCode(this)');
                    }
                }, 1000)
            }
            else if(stat.errcode == 4003){
                PICCODE_ERR = true;
                PICCODE_ERR_CONTENT = stat.errmsg;
                $('#mobile-err span').html(PICCODE_ERR_CONTENT);
                $('#mobile-err').show();
            }

            else{
                PICCODE_ERR = true;
                PICCODE_ERR_CONTENT = '验证码输入错误';
                $('#image-code-err span').html(PICCODE_ERR_CONTENT);
                $('#image-code-err').show();
                generateImageCode();
                $('.phonecode-a').attr('onclick', 'sendSMSCode(this)');
            }
        }
    })
}
// 主程序
$(function(){
    // 当用户输入手机号后开始进行判断
   $('#mobile').change(function(){
       // 错误时暂停程序
       if(!mobile_check()){
           $('#mobile-err').hide();
       }
   });
   // 用户输入图片验证码后， 错误提示信息隐藏
    $('#imagecode').change(function(){
        var piccode = $('#imagecode').val();
        if(piccode){
            $('#image-code-err').hide();
        }
    });
    $('#phonecode').change(function(){
        var phonecode = $('#phonecode').html();
        if(phonecode){
            $('#phone-code-err').hide();
        }
    })
    $('#password').change(function(){
        var passwd = $('#password').val();
        if(passwd){
            $('#password-err').hide();
        }
    })
    $('#password2').focus(function(){
        var passwd = $('#password').val();
        if(!passwd){
             PASSWORD_ERR = true;
             PASSWORD_ERR_CONTENT = '请输入密码';
             $('#password-err span').html(PASSWORD_ERR_CONTENT);
             $('#password-err').show();

        }
    })
    $('#password2').change(function(){
        var passwd2 = $('#password2').val();
        var passwd = $('#password').val();
        if(passwd2 && (passwd2 == passwd)){
            $('#password2-err').hide();
        }

    })
    // 初始化生成验证码图片
    generateImageCode();
    $('.form-register').submit(function(e){
        // 阻止form表单原来submit功能
        e.preventDefault();
        // 采用ajax传输
        // 判断手机号是否为空
        if(mobile_check()){
            return;
        }
        // 判断图片验证码是否为空
        var piccode = $('#imagecode').val();
        if(!piccode){
            PICCODE_ERR = true;
            PICCODE_ERR_CONTENT = '请输入验证码';
            $('#image-code-err span').html(PICCODE_ERR_CONTENT);
            $('#image-code-err').show();
            return;
        }
        // 判断手机验证码是否为空
        var phonecode = $('#phonecode').val();
        if(!phonecode){
            PHONECODE_ERR = true;
            PHONECODE_ERR_CONTENT = '请输入手机验证码';
            $('#phone-code-err span').html(PHONECODE_ERR_CONTENT);
            $('#phone-code').show();
            return;
        }
        // 判断密码 and 确认密码是否为空
        var password = $('#password').val();
        if(!password){
            PASSWORD_ERR = true;
            PASSWORD_ERR_CONTENT = '请输入密码';
            $('#password-err span').html(PASSWORD_ERR_CONTENT);
            $('#password-err').show();
            return;
        }
        var password2 = $('#password2').val();
        if(!password2){
            PASSWORD_ERR2 = true;
            PASSWORD_ERR2_CONTEN = '请输入确认密码';
            $('#password2-err span').html(PASSWORD_ERR2_CONTENT);
            $('#password2-err').show();
            return;
        }
        // 判断两者是否相等
        if(password != password2){
            PASSWORD_ERR2 = true;
            PASSWORD_ERR2_CONTENT = '两次密码输入不一致';
            $('#password2-err span').html(PASSWORD_ERR2_CONTENT);
            $('#password2-err').show();
            return;
        }
        var data = {};
        $('.form-register').serializeArray().map(function(x){data[x.name]=x.value})
        $.ajax({
            url: '/api/register',
            method: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            header: {
                'X-XSRFTOKEN': getCookie('_xsrf'),
            },
            success: function(stat){
                if(stat.errcode == 0){
                    window.location.href = '/register.html';
                }
                else if(stat.errcode == 4003){
                    PICCODE_ERR = true;
                    PICCODE_ERR_CONTENT = stat.errmsg;
                    $('#mobile-err span').html(PICCODE_ERR_CONTENT);
                    $('#mobile-err').show();
                }
                else{
                    PICCODE_ERR = true;
                    PICCODE_ERR_CONTENT = '验证码输入错误';
                    $('#image-code-err span').html(PICCODE_ERR_CONTENT);
                    $('#image-code-err').show();
                    generateImageCode();
                    $('.phonecode-a').attr('onclick', 'sendSMSCode(this)');
                }
            }
        })
    })

});

