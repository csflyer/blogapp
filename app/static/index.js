$('#validate_img').click((e)=> {
    let src = '/auth/validate_code?flag=' + Math.random();
    $('#validate_img').attr('src', src);
});

function request(url, data, success_str, show_error){
    $.post(url, data).done((data)=>{
        if(!data.error){
            if(success_str){
                alert(message);
            };
            location.reload();
        }
        else{
            if(show_error) {
                alert(data.message);
            };
        }
    })
};


$('#add_tag_btn').click((e)=>{
    var tag_name = document.querySelector('#add_tag_input').value;
    if(tag_name){
        $.post("/add-tag",{
            tag: tag_name
        }).done((data)=>{
                    if(!data.error){
                        $(`<option>${tag_name}</option>`).appendTo($('select'));
                        alert('添加成功!')
                    }
                    else{
                        alert(data.message);
                    }
            })
    }
});

function remove_comment_div(){
    $('#cancel-comment').remove();
    $('#comment-content').remove();
};

function comment_ajax(content, ref_id){
    let path = window.location.pathname;
    let api = `${path}/add_comment`;
    $.post(api, {
        content: content,
        ref_id: ref_id,
    }).done((data)=>{
        if(!data.error){
            location.reload();
        }
        else{
            alert(data.message);
        }
    })
};

function send_comment(){
    let comment = $('#comment-input').val();
    if(!comment){
        alert('评论为空!');
        return;
    }
    if(comment.length > 500){
        alert('评论字数过长!')
        return;
    }
    if($('#comment-content').parent().parent().attr('class') == 'comments'){
        comment_ajax(comment, '');
    }
    else{
        comment_ajax(comment, $('#comment-content').parent().attr('id'));
    }
};

$('.comment').click((event)=>{
    let target = $(event.target);
    let cancel_comment = `
           <span id="cancel-comment">取消回复</span>
        `;
    let send_comment = `
            <div id="comment-content" class="input-group">
                <input id='comment-input' type="text" class="form-control" placeholder="请输入评论...">
                <span class="input-group-btn">
                    <button id='send-content' class="btn btn-default" type="button" onclick="send_comment()">发送评论!</button>
                </span>
            </div>
        `;
    if(target.context.className == 'reply'){
        remove_comment_div();
        $(event.target).after($(cancel_comment));
        $(event.target.parentNode.parentNode.children[1]).after(send_comment);
    }
    else if(target.context.id == 'cancel-comment'){
        remove_comment_div();
        $($('.comments').children()[1]).append(send_comment);
    }
    event.stopPropagation();
});

$('.delete').click((event)=>{
    if(confirm('确认要删除该文章吗?')){
        let post_id = $(event.target).parent().parent().attr('id');
        request(``)
    }
});


