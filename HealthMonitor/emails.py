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
from loguru import logger


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
def send_manual_alert_email(position, first_data):
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    logger.info(f'数据库中最新一条数据的对象为：{first_data}')
    # body = f"""
    #             Monitoring Alert!
    #
    #             An elderly individual has experienced a fall, as detected by the accelerometer and gyroscope.
    #
    #             **Location:** {position}
    #
    #             **Environmental Conditions:**
    #             - Temperature: {environment_temperature}°C
    #             - Humidity: {environment_humidity}%
    #
    #             **Body Vital Signs:**
    #             - Temperature: {body_temperature}°C
    #             - Blood Oxygen Saturation: {blood_oxygen}%
    #             - Heart Rate: {heart_rate} bpm
    #
    #             Immediate attention is required. Please respond promptly.
    #         """
    send_mail(subject='Alert', to=to, body="body")


# 老人主动点击按钮解除告警
def send_manual_alert_clearance_email(position, first_data):
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    logger.info(f'数据库中最新一条数据的对象为：{first_data}')
    # body = f"""
    #             Monitoring Alert!
    #
    #             An elderly individual has experienced a fall, as detected by the accelerometer and gyroscope.
    #
    #             **Location:** {position}
    #
    #             **Environmental Conditions:**
    #             - Temperature: {environment_temperature}°C
    #             - Humidity: {environment_humidity}%
    #
    #             **Body Vital Signs:**
    #             - Temperature: {body_temperature}°C
    #             - Blood Oxygen Saturation: {blood_oxygen}%
    #             - Heart Rate: {heart_rate} bpm
    #
    #             Immediate attention is required. Please respond promptly.
    #         """
    send_mail(subject='Alert Clearance', to=to, body="body")


# 加速器和陀螺仪判断老人摔倒自动报警
def send_automatic_monitoring_alert_email(position, **kwargs):
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    logger.info(f"调用主动报警邮件：{kwargs}")

    body = f"""
                Monitoring Alert!

                An elderly individual has experienced a fall, as detected by the accelerometer and gyroscope.

                **Location:** {position}

                **Environmental Conditions:**
                - Temperature: {kwargs['temperature']}°C
                - Humidity: {kwargs['humidity']}%

                **Body Vital Signs:**
                - Temperature: {kwargs['temp']}°C
                - Blood Oxygen Saturation: {kwargs['spo2']}%
                - Heart Rate: {kwargs['bmp']} bpm

                Immediate attention is required. Please respond promptly.
            """

    send_mail(subject='Monitoring Alert', to=to, body=body)
