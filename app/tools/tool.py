# @Time : 2019-02-20 10:27 
# @Author : Crazyliu
# @File : tool.py


def get_form_error_message(form):
    for field, errors in form.errors.items():
        if len(errors) > 0:
            return errors[0]
    return ''
