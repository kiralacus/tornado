//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    $.get('/api/check_login', function(e){
        if(e.errcode=='0'){
            if(e.errmsg != '用户已通过验证') {
                window.location.href = '/auth.html';
            }
        }
        else if(e.errcode=='4101'){
            window.location.href = '/login.html';
        }
    });
    $.get("/api/order/guest", function(data){
        if(data.errcode == '0'){
            console.log(data);
            if(!data.order.length){
                $('.orders-list').html(template('orders-list-tmpl', {'orders': 0}));
            }
            else{
                $('.orders-list').html(template('orders-list-tmpl', {'orders': data.order}));
            }
        }
    });
    $('.order-accept').click(function(){
        alert(2);
        $this = $(this);
        var house_id = $(this).parent().parent().parent().attr('order-id');
        $('.modal-accept').on('click', function(){
            alert(1);
            var y_o_n = 1;
            var param = {
                y_o_n: y_o_n,
                house_id: house_id
            };
            $.ajax({
                url: '/api/order/guest',
                method: 'POST',
                headers: {
                    'X-XSRFTOKEN': getCookie('_xsrf'),
                },
                contentType: 'application/json',
                data: JSON.stringify(param),
                dataType: 'json',
                success: function(e){
                    if(e.errcode == '4101'){
                        window.location.href = '/login.html';
                    }
                    else if(e.errcode=='4104'){
                        window.location.href = '/auth.html';
                    }
                    else if(e.errcode == '0'){
                        $this.parent().hide();
                        $('#accept-modal').modal('hide');
                    }
                }
            })
        })
    })
});