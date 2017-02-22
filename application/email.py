import smtplib
from threading import Thread

import logging
from flask import current_app
from flask import render_template
from flask.ext.mail import Message

# def send_async_email(app, msg):
#     with app.app_context():
#         app.mail.send(msg)
#
#
# def send_email(to, subject, template, **kwargs):
#     app = current_app._get_current_object()
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
#                   sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)
#     thr = Thread(target=send_async_email, args=[app, msg])
#     thr.start()
#     return thr

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr, formatdate


def _format_addr(self, s):
    """
    :return: Alias_name <xxxx@example.com>
    """
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = MIMEMultipart()

    msg.attach(MIMEText(render_template(template + '.html', **kwargs), 'html', 'utf-8'))  # 纯文本

    msg['From'] = app.config['MAIL_SENDER']
    msg['To'] = to
    msg['Subject'] = subject
    msg['Date'] = formatdate()

    # =========================================================================
    # 发送邮件
    # =========================================================================
    try:
        # SMTP服务器设置(地址,端口):
        server = smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        # 连接SMTP服务器(发件人地址, 客户端授权密码)
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        # 发送邮件
        server.sendmail(app.config['ADMIN'], to, msg.as_string())

        logging.info('mail send success!')

    except smtplib.SMTPException as e:

        logging.info(str(e))
        print(e)
        logging.error('mail send error!')

    finally:
        # 退出SMTP服务器
        server.quit()
