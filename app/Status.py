# @Time : 2019-02-20 16:22 
# @Author : Crazyliu
# @File : Status.py
from flask_login import current_user
from functools import wraps
from flask import abort


class UserStatus:
    Unconfirmed = 'Unconfirmed'
    Normal = 'Normal'
    Forbidden = 'Forbidden'
    Auth = 'Auth'


class TokenString:
    Confirm = 'Confirm'
    ResetPassword = 'reset_password'
    ChangeEmail = 'change_email'
    NewEmail = 'new_email'


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTRATER = 0x80

    User = FOLLOW | COMMENT | WRITE_ARTICLES
    Moderator = User | MODERATE_COMMENTS
    Admin = ADMINISTRATER

    @staticmethod
    def Required(permission):
        def decorator(func):
            @wraps(func)
            def wrap(*args, **kwargs):
                if current_user.can(permission):
                    return func(*args, **kwargs)
                else:
                    abort(501)
            return wrap
        return decorator

