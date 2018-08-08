function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg(msg) {
    if(msg) {
        $('.popup_con .popup p').html(msg);
    }
    $('.popup_con').fadeIn();
    setTimeout(function(){
        $('.popup_con').fadeOut('fast');
    }, 1000)

}

$(document).ready(function(){
    var days = 0;
    var sd = '';
    var ed = '';
    var amount = 0;
    $.get('/api/check_login', function(e){
        if(e.errcode == '4101'){
            window.location.href = '/login.html';
        }
    });

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    // 判断时间选择是否正确
    // $('.input-daterange').click(function(){
    //     alert(2);
    //     sd = $('#start-date').val();
    //     ed = $('#end-date').val();
    //     if(!(sd || ed || sd <= ed )){
    //         console.log(sd, ed);
    //         console.log(sd || ed || sd <= ed);
    //         showErrorMsg();
    //         return;
    //     }
    //     else{
    //         start = new Date(sd);
    //         end = new Date(ed);
    //         days = (end - start)/(3600*24) + 1;
    //
    //     }
    // });



    var houseID = decodeQuery()['houseid'];
    $.get('/api/house/info?id='+houseID, function(e){
        console.log(e);
        if(e.errcode == '0'){
            $('.house-info img').attr('src', e.data.index_image);
            $('.house-text h3').html(e.data.title);
            $('.house-text span').html(e.data.price);
        }
    });

    $('#end-date').change(function(){
        sd = $('#start-date').val();
        ed = $('#end-date').val();
        if(!(sd || ed || sd <= ed )) {
            console.log(sd, ed);
            console.log(sd || ed || sd <= ed);
            showErrorMsg();
            return;
        }
        else{
            start = new Date(sd);
            end = new Date(ed);
        }
        var price = $('.house-text span').html();
        days = (end - start)/(1000*3600*24)+1;
        amount = days * price;
        console.log(amount);
        $('.order-amount span').html(amount.toFixed(2) + "(共"+ days +"晚)");
    });

    $('.submit-btn').click(function(){
        if(!amount){
            showErrorMsg('请填写入住时间');
            return;
        }
        // 防止重复提交
        if(amount) {
            $(this).prop('disable', true);
        }
        var content = {
            'start_date': sd,
            'end_date': ed,
           'house_id': houseID
        };
        $.ajax({
            url: '/api/order/book',
            method: 'POST',
            headers: {
                'X-XSRFTOKEN': getCookie('＿xsrf'),
            },
            data: JSON.stringify(content),
            contentType: 'application/json',
            dataType: 'json',
            success: function(e){
                if(e.errcode=='4101'){
                    window.location.href = '/login.html';
                }
                else if(e.errcode=='4004'){
                    showErrorMsg(e.errmsg);
                    $('.submit-btn').prop('disable', false);
                }
                else if(e.errcode=='0'){
                    window.location.href = '/orders.html';
                }
                else{
                    showErrorMsg('网络问题, 请重新提交');
                    window.location.reload();
                }
            }
        })

    })
})
