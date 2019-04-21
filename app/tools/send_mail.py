# @Time : 2019-02-20 14:23 
# @Author : Crazyliu
# @File : send_mail.py
from .. import mail
from flask import current_app, render_template
from flask_mail import Message
from threading import Thread


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

    Thread(target=mail.send, args=(msg,)).start()
    return




