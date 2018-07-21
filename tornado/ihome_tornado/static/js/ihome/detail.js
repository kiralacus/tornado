function hrefBack() {
    history.go(-1);
}

// 解析url, 获取URL中参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    var house_id = decodeQuery()["id"];
    var preurl = decodeQuery()['preurl'];
    // 获取房屋详细信息
    $.get('/api/house/detail?id='+house_id, function(e){
        $('.detail-con').html(template('house-detail-tmpl', {house: e.data}))
    })
    // 获取房屋图片
    $.get('/api/house/images?id='+house_id, function(e){
        $('.swiper-container').html(template('house-image-tmpl', {images: e.data}));
    })

    if(preurl == 'myhouse'){
        $('#form-house-image').show();
        $('.book-house').hide();
        $('#house-id').val(house_id);
        $('#form-house-image').submit(function(e){
            e.preventDefault();
            var options = {
                url: '/api/house/addimage',
                method: 'POST',
                headers:{
                  'X-XSRFOKEN': getCookie('_xsrf')
                },
                dataType: 'json',
                success: function(e){
                    if(e.errcode == '4101'){
                        window.location.href = '/login.html';
                    }
                    else if(e.errcode == '4104'){
                        alert('用户尚未通过验证')
                    }
                    else if(e.errcode == '0'){
                        $('#loadwaiting').fadeOut();
                        $('#loadsuccess').fadeIn(function() {
                            setTimeout(function () {
                                $('#loadsuccess').fadeOut();
                            }, 1000)
                        });
                        $('.swiper-wrapper').append('<li class="swiper-slider"><img src='+e.data+'></li>');
                    }
                }
            }
            $(this).ajaxSubmit(options);
        })
    }
})