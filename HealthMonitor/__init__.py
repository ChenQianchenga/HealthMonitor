# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：bluelog
# Name:__init__.py.py
# Description:
# Author:ChenQiancheng
# Date:2023/10/3  16:32
# --------------------------------------------------------------------------
import json
import os
from datetime import datetime

import requests
from flask_cors import CORS
import click
from flask import Flask, current_app
from HealthMonitor.blueprints import monitor
from HealthMonitor.blueprints.monitor import monitor_bp
from HealthMonitor.extensions import db, mail, moment, mqtt_client
from HealthMonitor.models import SensorData
from HealthMonitor.settings import config
from HealthMonitor.emails import send_manual_alert_email, send_manual_alert_clearance_email, send_email_test
from HealthMonitor.emails import send_automatic_monitoring_alert_email

# 百度地图逆地理编码API参数
BAIDU_API_URL = 'http://api.map.baidu.com/reverse_geocoding/v3/'
BAIDU_API_KEY = 'lHGem8BSeNkr84OOOaGDB0vdiHHpqGi8'
COORD_TYPE = 'wgs84ll'  # 使用WGS84坐标系，可根据实际情况修改


# 获取位置信息
def get_location_info(latitude, longitude):
    url = BAIDU_API_URL + '?ak=' + BAIDU_API_KEY + '&location=' + str(latitude) + ',' + str(
        longitude) + '&output=json&coordtype=' + COORD_TYPE
    print(url)
    response = requests.get(url)
    print("折柳", response.text)
    # data = response.json()
    # if data['status'] == 0:
    #     result = data['result']
    #     print(result)
    #     formatted_address = result['formatted_address']
    #     print('Formatted Address:', formatted_address)
    #     # 还可以获取其他详细信息，例如省份、城市、区县等
    #     # province = result['addressComponent']['province']
    #     # city = result['addressComponent']['city']
    #     # district = result['addressComponent']['district']
    #     # ...
    # else:
    #     print('Failed to get location info')


def gyro_is_fallen(gyro_data, threshold=45):
    angleX = gyro_data['gx']
    angleY = gyro_data['gy']
    angleZ = gyro_data['gz']
    print(abs(angleX))
    print(abs(angleY))
    if abs(angleX) > threshold or abs(angleY) > threshold:
        return True
    else:
        return False


def accel_is_fallen(accel_data, threshold=2.0):
    acceleration = accel_data
    x = acceleration["X"]
    y = acceleration["Y"]
    z = acceleration["Z"]

    # 计算合成加速度
    acceleration_magnitude = (x ** 2 + y ** 2 + z ** 2) ** 0.5

    # 判断是否满足跌倒条件
    print(acceleration_magnitude)
    if acceleration_magnitude > threshold:
        return True
    else:
        return False


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('HealthMonitor')
    # 引入配置
    app.config.from_object(config[config_name])
    CORS(app)  # 启用CORS
    # 注册日志处理器
    register_logging(app)
    # 注册扩展（扩展初始化）
    register_extension(app)
    # 注册蓝本
    register_blueprints(app)
    # 注册自定义shell命令
    register_commands(app)
    # 注册错误处理函数
    # register_errors(app)
    # 注册shell上下文处理函数
    register_shell_context(app)
    # 注册模板上下文处理函数
    # register_template_context(app)
    # 数据上报
    TOPIC = 'esp32/report/data'
    # 手动告警
    MANUAL_ALARM_MQTT_TOPIC = 'esp32/report/manual/alarm'
    # 自动告警
    AUTOMATIC_ALARM_MQTT_TOPIC = 'esp32/report/automatic/alarm'

    # 创建一个函数注册表，将topic与对应的操作函数关联起来
    topic_handlers = {}

    # 注册手动触发告警和解除告警操作函数
    # 我在这里： {'action': False, 'alert_time': '2024-03-03 22:45:38'}
    def handle_manual_alert(payload_dict):
        # 判断是告警发生还是解除
        if payload_dict['action']:
            # 告警发生
            send_manual_alert_email()
        else:
            send_manual_alert_clearance_email()

    topic_handlers[MANUAL_ALARM_MQTT_TOPIC] = handle_manual_alert

    # 注册自动告警发生操作函数
    def handle_auto_alert(payload_dict):
        print(payload_dict)

    topic_handlers[AUTOMATIC_ALARM_MQTT_TOPIC] = handle_auto_alert

    # 默认操作函数，处理数据上报topic
    def handle_default(payload_dict, topic, payload):
        time_str = payload_dict['report_time']

        # 将时间字符串转换为 datetime 对象
        report_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        # 创建一个 SensorData 对象并设置 report_time 字段
        # 创建 SensorData 对象并保存到数据库
        if gyro_is_fallen(payload_dict) and accel_is_fallen(payload_dict):
            print("老人跌倒告警")
            # send_automatic_monitoring_alert_email()
        # 获取位置信息
        # latitude_data = payload_dict['latitude']
        # longitude_data = payload_dict['longitude']
        # 转换经纬度

        # 打印转换结果
        # print('Converted Latitude:', converted_lat)
        # print('Converted Longitude:', converted_lon)
        # get_location_info(latitude=converted_lat, longitude=converted_lon)
        # latitude=latitude_data, longitude=longitude_data,
        data = SensorData(report_time=report_time,
                          environment_temperature=payload_dict['environment_temperature'],
                          humidity=payload_dict['humidity'], topic=topic, payload=payload)
        db.session.add(data)
        db.session.commit()

    @mqtt_client.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            print('连接mqtt服务器成功')
            mqtt_client.subscribe(TOPIC)  # 订阅上报数据主题
            mqtt_client.subscribe(MANUAL_ALARM_MQTT_TOPIC)  # 订阅手动告警
            mqtt_client.subscribe(AUTOMATIC_ALARM_MQTT_TOPIC)  # 订阅自动告警
        else:
            print('Bad connection. Code:', rc)

    @mqtt_client.on_message()
    def handle_message(client, userdata, message):
        with app.app_context():
            topic = message.topic
            payload = message.payload.decode()
            print(topic)
            print(payload)
            payload_dict = json.loads(payload)
            # 检查是否存在与当前topic关联的操作函数
            if topic in topic_handlers:
                # 调用与当前topic关联的操作函数，并传递payload_dict作为参数
                topic_handlers[topic](payload_dict)
            else:
                # 如果没有与当前topic关联的操作函数，则使用默认操作函数处理数据
                handle_default(payload_dict, topic, payload)

    return app


def register_logging(app):
    pass


def register_extension(app):
    # bootstrap.init_app(app)
    db.init_app(app)
    # ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    mqtt_client.init_app(app)

    # login_manager.init_app(app)
    # csrf.init_app(app)


def register_blueprints(app):
    app.register_blueprint(monitor_bp)
    # app.register_blueprint(admin_bp, url_prefix='/admin')
    # app.register_blueprint(auth_bp, url_prefix='/auth')


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        pass
        # admin = Admin.query.first()
        # categories = Category.query.order_by(Category.name).all()
        # if current_user.is_authenticated:
        #     unread_comments = Comment.query.filter_by(reviewed=False).count()
        # else:
        #     unread_comments = None
        # return dict(admin=admin, categories=categories, unread_comments=unread_comments)


# def register_errors(app):
#     @app.errorhandler(400)
#     def bad_request(e):
#         return render_template('errors/400.html'), 400
#
#     @app.errorhandler(CSRFError)
#     def handle_csrf_error(e):
#         return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def initdb(drop):
        if drop:
            click.confirm("确定继续删除全部数据库表？", abort=True)
            db.drop_all()
            click.echo("删除数据库表")
        db.create_all()
        click.echo("初始化数据库成功！")


def register_shell_context(app):
    pass
