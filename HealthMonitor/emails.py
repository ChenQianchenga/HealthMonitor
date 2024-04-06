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
    print(first_data.report_time)
    body_html = f"""\
        <html>
            <head></head>
            <body>
                <h1>Monitoring Alert!</h1>

                <p>An elderly individual has experienced a fall, as detected by the accelerometer and gyroscope.</p>

                <h2>Time of Occurrence:</h2>
                <p>{first_data.report_time}</p>

                <h2>Location:</h2>
                <p>{position}</p>

                <h2>Environmental Conditions:</h2>
                <ul>
                    <li><strong>Temperature:</strong> {first_data.environment_temperature}&deg;C</li>
                    <li><strong>Humidity:</strong> {first_data.humidity}%</li>
                </ul>

                <h2>Body Vital Signs:</h2>
                <ul>
                    <li><strong>Temperature:</strong> {first_data.temperature}&deg;C</li>
                    <li><strong>Blood Oxygen Saturation:</strong> {first_data.blood_oxygen}%</li>
                    <li><strong>Heart Rate:</strong> {first_data.heart_rate} bpm</li>
                </ul>

                <p>Immediate attention is required. Please respond promptly.</p>
            </body>
        </html>
        """
    send_mail(subject='Alert', to=to, body=body_html)


# 老人主动点击按钮解除告警
def send_manual_alert_clearance_email(position, first_data):
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    logger.info(f'数据库中最新一条数据的对象为：{first_data}')
    body_html = f"""\
            <html>
            <head>
                <title>Monitoring Alert!</title>
            </head>
            <body>
                <h1>Monitoring Alert!</h1>
                <p>An elderly individual has experienced a fall, as detected by the accelerometer and gyroscope.</p>

                <h2>Time of Occurrence:</h2>
                <p>{first_data.report_time}</p>

                <h2>Location:</h2>
                <p>{position}</p>

                <h2>Environmental Conditions:</h2>
                <ul>
                    <li>Temperature: {first_data.environment_temperature}&deg;C</li>
                    <li>Humidity: {first_data.humidity}%</li>
                </ul>

                <h2>Body Vital Signs:</h2>
                <ul>
                    <li>Temperature: {first_data.temperature}&deg;C</li>
                    <li>Blood Oxygen Saturation: {first_data.blood_oxygen}%</li>
                    <li>Heart Rate: {first_data.heart_rate} bpm</li>
                </ul>

                <p><strong>Immediate attention is required. Please respond promptly.</strong></p>
            </body>
            </html>
        """
    send_mail(subject='Alert Clearance', to=to, body=body_html)


# 加速器和陀螺仪判断老人摔倒自动报警
def send_automatic_monitoring_alert_email(position, **kwargs):
    to = ['1025212193@qq.com', '986508902@qq.com', '404413567@qq.com']
    logger.info(f"调用主动报警邮件：{kwargs}")

    html_body = f"""
            <html>
                <head>
                    <style>
                        h1 {{ color: red; font-weight: bold; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                    </style>
                </head>
                <body>
                    <h1>Monitoring Alert!</h1>
                    <p>An elderly individual has experienced a fall, as detected by the accelerometer and gyroscope.</p>

                    <table>
                        <tr>
                            <th>Time of Occurrence</th>
                            <td>{kwargs['report_time']}</td>
                        </tr>
                        <tr>
                            <th>Location</th>
                            <td>{position}</td>
                        </tr>
                    </table>

                    <h2>Environmental Conditions:</h2>
                    <ul>
                        <li>Temperature: {kwargs['environment_temperature']}&deg;C</li>
                        <li>Humidity: {kwargs['humidity']}%</li>
                    </ul>

                    <h2>Body Vital Signs:</h2>
                    <ul>
                        <li>Temperature: {kwargs['temp']}&deg;C</li>
                        <li>Blood Oxygen Saturation: {kwargs.get('sop2', None)}%</li>
                        <li>Heart Rate: {kwargs['bmp']} bpm</li>
                    </ul>

                    <p><strong>Immediate attention is required. Please respond promptly.</strong></p>
                </body>
            </html>
        """

    send_mail(subject='Monitoring Alert', to=to, body=html_body)
