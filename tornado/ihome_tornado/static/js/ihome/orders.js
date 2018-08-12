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
        if(e.errcode == '4101'){
            window.location.href = '/login.html';
        }
    });
    $.get('/api/order/my', function(e){
        if(e.errcode == '0'){
            if(e.order.length){
                $('.orders-list').html(template('orders-list-tmpl', {'orders': e.order}));
            }
            else{
                $('.orders-list').html(template('orders-list-tmpl', {'orders': 0}));
            }
            $('.order-comment').on('click', function(){
                var $this = $(this);
                var order_id = $this.parent('div').parent('div').parent('li').attr('order-id');
                $('.modal-comment').on('click', function(){
                    var comment = $('.form-control').val();
                    var param = {
                        'order_id': order_id,
                        'comment': comment,
                    };
                    $.ajax({
                        url: '/api/order/my',
                        method: 'POST',
                        headers: {
                            'X-XSRFTOKEN': getCookie('_xsrf'),
                        },
                        data: JSON.stringify(param),
                        contentType: 'application/json',
                        dataType: 'json',
                        success: function(e){
                            if(e.errcode == '4101'){
                                window.location.href = '/login.html';
                            }
                            else if(e.errcode == '0'){
                                $('#comment-modal').modal('hide');
                                $this.parent('div').hide();
                                $this.parent().parent().next().children('div').children('ul').children('li').eq(4).children('span').html('已完成');
                            }
                        }
                    })
                });
            })
        }
    })
});