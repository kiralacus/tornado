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
    var sd = $('#start-date').val().substr(5);
    var ed = $('#end-date').val().substr(5);
    if(sd){
        $('.filter-title-bar .filter-title').eq(0).children().eq(0).html(sd + ' | ' + ed)
    }
}
// 更新页面信息
function updateHouseData(action="append") {
    var sd = $('#start-date').val();
    var ed = $('#end-date').val();
    var aid = $('.filter-area li').filter('.active').attr('area-id');
    var sk = $('.filter-sort li').filter('.active').attr('sort-key');
    var p = next_page;
    if(action == 'renew'){
        p = 1;
    }
    var param = {
        sd: sd,
        ed: ed,
        aid: aid,
        sk: sk,
        p: p
    };

    $.get('/api/house/list', param, function(e){
        if(e.errcode == '0'){
            console.log(e);
            if(e.total_page){
                if(action == 'renew'){
                    $('.house-list').html(template('house-list-tmpl', {houses: e.houses}));
                    cur_page = 1;
                    next_page = 1;
                    total_page = e.total_page;
                }
                else if(action == 'append'){
                    cur_page = next_page;
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
    var sd = param['sd'];
    var ed = param['ed'];
    var aid = param['aid'];
    if(sd){
        $('#start-date').val(sd);
        $('#end-date').val(ed);
    }
    updateFilterDateDisplay();
    $.get("/api/house/area", function(data){
        house_data_querying = false;
        if(data.errcode == '0'){
            console.log(data);
            if(aid) {
                $('.filter-area').html(template('filter-area-tmpl', {areas: data.data, active_id: aid}));
            }
            else{
                $('.filter-area').html(template('filter-area-tmpl', {areas: data.data}));
            }
            updateHouseData('renew');
            $('.filter-area li').on('click', function(){
                if(!$(this).hasClass('active')){
                    $(this).addClass('active').siblings().removeClass('active');
                }
                else{
                    $(this).removeClass('active');
                    $('.filter-title').eq(1).children('span').eq(0).html('位置区域')
                }
            });
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
            };
        }
    });
    $('filter-title').eq(1).click(function(){
        $(this).children('span').children('i').attr('class', 'fa fa-angle-up');

    });

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });

    $('.filter-title-bar').on('click', '.filter-title', function(e){
        var index = $(this).index();
        var $filter_item = $('.filter-item');
        if($filter_item.eq(index).hasClass('active')){
            $filter_item.eq(index).removeClass('active');
            $filter_item.eq(index).children('span').children('i').attr('class', 'fa fa-angle-down');
            $('.display-mask').hide();
        }
        else{
            $filter_item.eq(index).addClass('active').siblings().removeClass('active');
            $filter_item.eq(index).children('span').children('i').attr('class', 'fa fa-angle-up');
            $filter_item.eq(index).siblings().children('span').children('i').attr('class', 'fa fa-angle-down');
            $('.display-mask').show();
        }
    });

    $('.display-mask').on('click', function(){
        $('.filter-item').removeClass('active');
        $(this).hide();
        updateFilterDateDisplay();
        updateHouseData('renew');
    });



    $('.filter-sort li').on('click', function(){
        if(!$(this).hasClass('active')) {
            $(this).addClass('active').siblings().removeClass('active');
        }
    })
});