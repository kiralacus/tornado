function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
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
    $.get("/api/house/info?id="+house_id, function (data) {
        if ("0" == data.errcode) {
            if(!data.data.images.length){
                $('.swiper-container').hide();
            }
            else {
                $(".swiper-container").html(template("house-image-tmpl", {
                    "img_urls": data.data.images,
                    "price": data.data.price
                }));
                $(".detail-con").html(template("house-detail-tmpl", {"house":data.data}));
                var mySwiper = new Swiper('.swiper-container', {
                    loop: true,
                    autoplay: 2000,
                    autoplayDisableOnInteraction: false,
                    pagination: '.swiper-pagination',
                    paginationType: 'fraction'
                })
            }
        }
    }, "json");

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
            };
            $(this).ajaxSubmit(options);
        })
    }
})
// function hrefBack() {
//     history.go(-1);
// }
//
// function decodeQuery(){
//     var search = decodeURI(document.location.search);
//     return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
//         values = item.split('=');
//         result[values[0]] = values[1];
//         return result;
//     }, {});
// }
//
// $(document).ready(function(){
//     var house_id = decodeQuery()["id"];
//     $.get("/api/house/detail?id="+house_id, function (data) {
//         if ("0" == data.errcode) {
//             // $(".swiper-container").html(template("house-image-tmpl", {"img_urls":data.data.images, "price":data.data.price}));
//             $(".detail-con").html(template("house-detail-tmpl", {"house":data.data}));
//             var mySwiper = new Swiper ('.swiper-container', {
//                 loop: true,
//                 autoplay: 2000,
//                 autoplayDisableOnInteraction: false,
//                 pagination: '.swiper-pagination',
//                 paginationType: 'fraction'
//             })
//             // data.user_id为访问页面用户,data.data.user_id为房东
//             // if (data.user_id != data.data.user_id) {
//             //     $(".book-house").attr("href", "/booking.html?hid="+house_id);
//             //     $(".book-house").show();
//             // }
//         }
//     }, "json")
// })