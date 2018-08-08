var cur_page = 1;
var next_page = 1;
var total_page = 1;
var house_data_querying = true;

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function updateFilterDateDisplay() {
    var sd = $('#start-date').value();
    var ed = $('#end-date').value();
    if(sd){
        $('.filter-title-bar .filter-title').eq(0).children().eq(0).html(sd + ' | ' + ed)
    }
}
// 更新页面信息
function updateHouseData(action="append") {
    var sd = $('#start-date').value();
    var ed = $('#end-date').value();
    var aid = $('.filter-area .active').attr('area-id');
    var sk = $('.filter-sort .active').html();
    var p = next_page;
    var param = {
        sd: sd,
        ed: ed,
        aid: aid,
        sk: sk,
        p: p
    };

    $.get('/api/house/list', param, function(e){
        if(e.errcode == '0'){
            if(e.total_page){
                if(action == 'renew'){
                    $('.house-list').html(template('house-list-tmpl', {houses: e.houses}));
                }
                else if(action == 'append'){
                    $('.house-list').append(template('house-list-tmpl', {houses: e.houses}));
                }
            }
            else{
                $('.house-list').html('没有符合要求的住房')
            }
        }
    })
}

$(document).ready(function(){
    var param = decodeQuery();
    sd = param['sd'];
    ed = param['ed'];
    aid = param['aid'];
    $.get("/api/house/area", function(data){

            var windowHeight = $(window).height();
            window.onscroll=function(){
                // var a = document.documentElement.scrollTop==0? document.body.clientHeight : document.documentElement.clientHeight;
                var b = document.documentElement.scrollTop==0? document.body.scrollTop : document.documentElement.scrollTop;
                var c = document.documentElement.scrollTop==0? document.body.scrollHeight : document.documentElement.scrollHeight;
                if(c-b<windowHeight+50){
                    if (!house_data_querying) {
                        house_data_querying = true;
                        if(cur_page < total_page) {
                            next_page = cur_page + 1;
                            updateHouseData();
                        }
                    }
                }
            }
        }
    });


    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function(e){
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
            cur_page = 1;
            next_page = 1;
            total_page = 1;
            updateHouseData("renew");
        }
    });
    $(".display-mask").on("click", function(e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        cur_page = 1;
        next_page = 1;
        total_page = 1;
        updateHouseData("renew");
    });
    $(".filter-item-bar>.filter-area").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })
})