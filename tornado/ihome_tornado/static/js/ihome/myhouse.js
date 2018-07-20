$(document).ready(function(){
    $.get('/api/house/myhouse', function(data){
        if(data.errcode == '0'){
            console.log(data);
            $('.houses-list').html(template('house-list-tmpl', {houses: data.data}))
        }
        else if(data.errcode == '4101'){
            window.location.href = '/login.html';
        }
        else if(data.errcode == '4101'){
            $('.house-list .auth-warn').show();
            $('#houses-list').hide();
        }
    })
})