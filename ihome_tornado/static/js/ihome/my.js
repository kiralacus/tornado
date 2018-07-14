function logout() {
    $.get("/api/logout", function(data){
        if (0 == data.errcode) {
            alert(1);
            window.location.href='/'
        }
        else if(4101 == data.errcode){
            window.location.href='/login.html'
        }
        else{
            alert('登出失败')
        }
    })
}

$(document).ready(function(){
    $.get('/api/profile', function(e){
        if(e.errcode == 0){
            $('#user-avatar').attr('src', e.data.avatar);
            $('#user-name').html(e.data.up_name);
            $('#user-mobile').html(e.data.up_mobile);
        }
        else if(e.errcode == 4101){
            window.location.href = '/login.html';
        }
    })
});