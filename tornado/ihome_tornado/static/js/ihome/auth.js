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

$(document).ready(function(){
    $('#real-name').change(function(){
        checkInfo();
    })
    $('#id-card').change(function(){
        checkInfo();
    })

    $.get('/api/profile/auth', function(e){
        if(e.errcode == 0){
            $('#real-name').attr('placeholder', e.data.up_real_name);
            $('#id-card').attr('placeholder', e.data.up_id_card);
            $('.btn-success').remove();
        }
        else if(e.errcode == 4101){
            window.location.href = '/login.html';
        }
        else if(e.errcode == 4104){
            $('#real-name').attr('placeholder', '此处必须填写');
            $('#id-card').attr('placeholder', '此处必须填写');
        }
    })

    $('#form-auth').submit(function(e){
        e.preventDefault();
        // 判断数据是否完整
        var name = $('#real-name').val();
        var id = $('#id-card').val();
        if(!(name && id)){
            $('.error-msg').show();
        }

        var data = {};
        $(this).serializeArray().map(function(x){data[x.name]=x.value});
        $.ajax({
            url: '/api/profile/auth',
            method: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(data),
            header: {
                'X-XSRFTOKEN': getCookie('_xsrf'),
            },
            success: function(e){
                if(e.errcode == 4101){
                    window.location.href = '/login.html';
                }
                else if(e.errcode == 0){
                   $('.popup_con').fadeIn('fast', function(){
                        setTimeout(function(){
                            $('.popup_con').fadeOut('fast');
                            $('.btn-success').remove();
                        }, 2000)
                    })
                }
            }
        })
    })
});
// 用于检查信息填写是否完整
function checkInfo(){
    var name = $('#real-name').val();
    var id = $('#id-card').val();
    if(name && id){
        $('.error-msg').hide();
    }
}

