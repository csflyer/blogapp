$('validate_img').click(()=> {
    let src = '/auth/validate_code?flag=' + Math.random();
    $('validate_img').attr('src', src);
})