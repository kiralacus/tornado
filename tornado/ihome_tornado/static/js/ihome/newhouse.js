function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.checkbox input').click(function(){
        checkFunc()
    })
    $("#area-id").attr('onchange', 'checkFunc()');

    $.get("/api/house/area", function (data) {
        if ("0" == data.errcode) {
            console.log(data);
            $('#area-id').html(template('area-tmpl', {areas: data.data}))
        }
        else if('4101' == data.errcode){
            window.location.href = '/login.html';
        }
    })
    $('#form-house-info').submit(function(e){
        e.preventDefault();
        // 由于浏览器可以帮助我们控制除了两个选项外的input不能为空， 因此我们只需要判断那两个选项是否为空
        if(!($('#area-id').val() && $('.checkbox input:checked').val())){
            $('.error-msg').show();
            return;
        }
        else{
            $('.error-msg').hide();
            data = {};
            $(this).serializeArray().map(function(x){
                data[x,name] = data[x.value];
                console.log(x);
            })
            $.ajax({
                url: '/api/house/info',
                method: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data),
                header: {
                    'X-XSRFTOKEN': getCookie('_xsrf'),
                },
                success: function(data){
                    if(data.errcode == 0){
                        $('#form-house-info').hide();
                        $('#form-house-image').show();
                    }
                    else if(data.errcode == '4101'){
                        window.location.href = '/login.html';
                    }
                    else{
                        alert('系统出错， 请重新提交')
                    }

                }
            })
        }

    })
});

function checkFunc(){
    if($('#area-id').val() && $('.checkbox input').val()){
        $('.error-msg').hide();
    }
}