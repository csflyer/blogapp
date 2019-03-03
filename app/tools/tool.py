# @Time : 2019-02-20 10:27 
# @Author : Crazyliu
# @File : tool.py

from flask import flash


class FlashMsg:
    info = lambda message: flash(message, category="info")
    error = lambda message: flash(message, category="error")
    warning = lambda message: flash(message, category="warning")
    message = lambda message: flash(message, category="message")


def get_form_error_message(form):
    for field, errors in form.errors.items():
        if len(errors) > 0:
            return errors[0]
    return ''





