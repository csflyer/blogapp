$('#validate_img').click((e)=> {
    let src = '/auth/validate_code?flag=' + Math.random();
    $('#validate_img').attr('src', src);
})