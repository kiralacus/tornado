function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $('.checkbox input').click(function () {
        checkFunc()
    })
    $("#area-id").attr('onchange', 'checkFunc()');

    $.get("/api/house/area", function (data) {
        if ("0" == data.errcode) {
            $('#area-id').html(template('area-tmpl', {areas: data.data}))
        }
        else if ('4101' == data.errcode) {
            window.location.href = '/login.html';
        }
    })
    var houseID = 0;
    $('#form-house-info').submit(function (e) {
        e.preventDefault();
        // 由于浏览器可以帮助我们控制除了两个选项外的input不能为空， 因此我们只需要判断那两个选项是否为空

        if (!($('#area-id').val() && $('.checkbox input:checked').val())) {
            $('.error-msg').show();
            return;
        }
        else {
            $('.error-msg').hide();
            var data = {};
            var facility = [];
            $(this).serializeArray().map(function (x) {
                if (x.name == 'facility') {
                    facility.push(x.value);
                }
                else {
                    data[x.name] = x.value;
                }
            })
            data['facility'] = facility;
            console.log(JSON.stringify(data));
            $.ajax({
                url: '/api/house/info',
                method: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data),
                header: {
                    'X-XSRFTOKEN': getCookie('_xsrf'),
                },
                success: function (data) {
                    console.log(data);
                    if (data.errcode == 0) {
                        $('#form-house-info').hide();
                        $('#form-house-image').show();
                        houseID = data.data.houseID;
                    }
                    else if (data.errcode == '4101') {
                        window.location.href = '/login.html';
                    }
                    else {
                        alert('系统出错， 请重新提交')
                    }

                }
            })
        }
    })

    $("#form-house-image").submit(function(e){
        e.preventDefault();
        $('#loadwaiting').fadeIn();
        var options = {
            url: '/api/house/image?houseid='+houseID,
            method: 'POST',
            dataType: 'json',
            headers: {
               'X-XSRFTOKEN': getCookie('_xsrf')
            },
            success: function(e){
                if(e.errcode == '0'){
                    $('#loadwaiting').fadeOut();
                    $('#loadsuccess').fadeIn(function(){
                        setTimeout(function(){
                            $('#loadsuccess').fadeOut();
                        }, 1000)
                    })
                    $('.house-image-cons').html('<img src='+e.data.url+'>')
                }
                else if(e.errcode == '4101'){
                    window.location.href='/login.html';
                }
            }
        };
        $(this).ajaxSubmit(options);
    })

})

function checkFunc(){
    if($('#area-id').val() && $('.checkbox input').val())
        $('.error-msg').hide();

}