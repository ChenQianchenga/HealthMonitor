# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
# ProjectName：bluelog
# Name:emails.py
# Description: 存储发送电子邮件的函数
# Author:ChenQiancheng
# Date:2023/10/3  16:04
# --------------------------------------------------------------------------
import random
import string
from threading import Thread
from flask import current_app
from flask_mail import Message
from HealthMonitor.extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, body):
    app = current_app._get_current_object()
    message = Message(subject, recipients=to, body=body)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


# 老人主动点击按钮触发告警
def send_manual_alert_email():
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    send_mail(subject='Alert', to=to, body='Alert! An alert has been triggered by the elderly.')


# 老人主动点击按钮解除告警
def send_manual_alert_clearance_email():
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    send_mail(subject='Alert Clearance', to=to,
              body='Alert cleared! The alerted condition has been resolved by the elderly.')


def send_email_test():
    recipients = ['986508902@qq.com', '404413567@qq.com']  # 多个收件人地址
    source = string.digits * 4
    captcha = random.sample(source, 4)
    captcha = "".join(captcha)
    message = Message(subject="知了传课注册验证码", recipients=recipients, body=f"告警了啊啊啊啊：{captcha}")
    mail.send(message=message)
    print("邮件已经发送")


# 加速器和陀螺仪判断老人摔倒自动报警
def send_automatic_monitoring_alert_email():
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    send_mail(subject='Monitoring Alert', to=to,
              body='Monitoring alert! Accelerometer and gyroscope have detected a fall by the elderly.')
