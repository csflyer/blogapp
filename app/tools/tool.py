# @Time : 2019-02-20 10:27 
# @Author : Crazyliu
# @File : tool.py

from flask import flash, current_app, request
from flask_login import current_user


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


class Log:
    @classmethod
    def baselog(cls, log_func, message):
        if not current_user.is_anonymous:
            log_func(' User : {} '.format(current_user.email) + ' Host : {} '.format(request.remote_addr) + message)
        else:
            log_func(' Host : {} '.format(request.remote_addr) + message)

    @classmethod
    def info(cls, message):
        cls.baselog(current_app.logger.info, message)

    @classmethod
    def warning(cls, message):
        cls.baselog(current_app.logger.warning, message)

    @classmethod
    def error(cls, message):
        cls.baselog(current_app.logger.error, message)





