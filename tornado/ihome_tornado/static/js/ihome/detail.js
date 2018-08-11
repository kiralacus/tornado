
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
            $('.book-house').attr('href', '/booking.html?id='+ house_id);
            console.log(data);
            if(!data.data.comments.content){
                $('.house-info').hide();
            };

            $(".swiper-container").html(template("house-image-tmpl", {
                "img_urls": data.data.images,
                "price": data.data.price
            }));
            $(".detail-con").html(template("house-detail-tmpl", {"house":data.data}));
            $('.house-comment-list').html(template('house-comment-list-tmpl', {"comment": data.data.comments}));
            var mySwiper = new Swiper('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            })
            if(!data.data.images.length){
                $('.swiper-container').hide();
            }
            var dictionary = {
                1: "无线网络",
                2: "热水淋浴",
                3: "空调",
                4: "暖气",
                5: "允许吸烟",
                6: "饮水设备",
                7: "牙具",
                8: "香皂",
                9: "拖鞋",
                10: "手纸",
                11: "毛巾",
                12: "沐浴露、洗发露",
                13: "冰箱",
                14: "洗衣机",
                15: "电梯",
                16: "允许做饭",
                17: "允许带宠物",
                18: "允许聚会",
                19: "门禁系统",
                20: "停车位",
                21: "有线网络",
                22: "电视",
                23: "浴缸"
            };
            var dictionary_en = {
                1: 'wirelessnetwork-ico',
                2: 'shower-ico',
                3: 'aircondition-ico',
                4: 'heater-ico',
                5: 'smoke-ico',
                6: 'drinking-ico',
                7: 'brush-ico',
                8: 'soap-ico',
                9: 'slippers-ico',
                10: 'toiletpaper-ico',
                11: 'towel-ico',
                12: 'toiletries-ico',
                13: 'icebox-ico',
                14: 'washer-ico',
                15: 'elevator-ico',
                16: 'iscook-ico',
                17: 'pet-ico',
                18: 'meet-ico',
                19: 'accesssys-ico',
                20: 'parkingspace-ico',
                21: 'wirednetwork-ico',
                22: 'tv-ico',
                23: 'hotbathtub-ico',
            };

            for(var i=1; i<24; i++){
                if(data.data.facility.indexOf(i)>=0){
                    $('.house-facility-list').append('<li><span class="'+ dictionary_en[i] +'"></span>'+ dictionary[i] +'</li>');
                }
                else{
                    $('.house-facility-list').append('<li><span class="jinzhi-ico"></span>'+dictionary[i]+'</li>')
                }
            }
        }
    }, "json");

    if(preurl == 'myhouse'){
        $('#form-house-image').show();
        $('.book-house').hide();
        $('#house-id').val(house_id);
        $('#form-house-image').submit(function(e){
            e.preventDefault();
           if(!$('#house-image').val()){
                alert('请添加照片');
                return;
            }
            if($('.swiper-container li').length >= 5){
                alert('已达照片上限');
                $('#form-house-image').hide();
                return;
            }

            $('#loadwaiting').fadeIn();
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
                                window.location.reload();
                            }, 1000)
                        });
                    }
                }
            };
            $(this).ajaxSubmit(options);
        })
    }
    else{
        $('#form-house-image').hide();
        $('.book-house').fadeIn();

    }
})
