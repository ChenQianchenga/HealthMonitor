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
from urllib import parse

import numpy as np
import requests
from flask_cors import CORS
import click
from flask import Flask, current_app
from HealthMonitor.blueprints import monitor
from HealthMonitor.blueprints.monitor import monitor_bp
from HealthMonitor.extensions import db, mail, moment, mqtt_client
from HealthMonitor.models import SensorData
from HealthMonitor.settings import config
from HealthMonitor.emails import send_manual_alert_email, send_manual_alert_clearance_email
from HealthMonitor.emails import send_automatic_monitoring_alert_email
from loguru import logger

# 百度地图逆地理编码API参数
BAIDU_API_URL = 'https://api.map.baidu.com/reverse_geocoding/v3/'
BAIDU_API_KEY = 'aujGhARF3F8jw5c4p7nViTcC7voXmwd3'
COORD_TYPE = 'wgs84ll'  # 使用WGS84坐标系，可根据实际情况修改


# 通过地址获取经纬度信息
def get_coordinates(address):
    # 对地址进行URL编码
    encoded_address = parse.quote(address)

    # 构建请求URL
    url = f'https://api.map.baidu.com/geocoding/v3/?address={encoded_address}&output=json&ak={BAIDU_API_KEY}'

    # 发送请求并获取响应
    response = requests.get(url)
    data = response.json()
    logger.info(f"地址详细信息：{data}")

    # 解析响应数据
    if data['status'] == 0:
        location = data['result']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        return None


# 获取位置信息
def get_location_info(latitude, longitude):
    url = BAIDU_API_URL + '?ak=' + BAIDU_API_KEY + '&location=' + str(latitude) + ',' + str(
        longitude) + '&output=json&coordtype=' + COORD_TYPE
    print(url)
    response = requests.get(url)
    print("折柳", response.text)


# 预处理数据
def preprocess_data(raw_data):
    expected_keys = ['humidity', 'report_time', 'environment_temperature', 'gx', 'gy', 'gz', 'X', 'Y', 'Z',
                     'temp', 'bmp', 'sop2']
    processed_data = {}

    for key in expected_keys:
        if key in raw_data:
            processed_data[key] = raw_data[key]
        else:
            processed_data[key] = None  # 或者设定其他默认值，如0、NaN等

    return processed_data


# 陀螺仪判断是否跌倒，阈值threshold
def gyro_is_fallen(gyro_data, threshold=45):
    angleX = gyro_data['gx']
    angleY = gyro_data['gy']
    angleZ = gyro_data['gz']
    logger.debug(f"angleX绝对值为：{abs(angleX)}")
    logger.debug(f"angleY绝对值为：{abs(angleY)}")
    if abs(angleX) > threshold or abs(angleY) > threshold:
        return True
    else:
        return False


# 加速度判断是否跌倒，阈值threshold

def accel_is_fallen(accel_data, threshold=200):
    try:
        first_data = SensorData.query.order_by(SensorData.report_time.desc()).first()
        old_x = first_data.acceleration_x
        old_y = first_data.acceleration_y
        old_z = first_data.acceleration_z
    except Exception as e:
        logger.error(e)
        return False
    acceleration = accel_data
    x = acceleration["X"]
    y = acceleration["Y"]
    z = acceleration["Z"]

    delta_x = abs(x - old_x)
    delta_y = abs(y - old_y)
    delta_z = abs(z - old_z)
    logger.debug(f"delta_x:{delta_x},delta_y:{delta_y},delta_z:{delta_z}")
    if delta_x > threshold or delta_y > threshold or delta_z > threshold:
        logger.error("加速度判断跌倒")
        return True
    else:
        return False


address = '河南省安阳市文峰区弦歌大道436号'


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
        # 这个地方去查一下数据库
        try:
            first_data = SensorData.query.order_by(SensorData.report_time.desc()).first()
            print(first_data)
        except AttributeError:
            return False
        logger.info(f"当前主动发生告警，数据库最新一条数据：{first_data}")
        # 判断是告警发生还是解除
        if payload_dict['action']:
            # 告警发生
            logger.info(f"手动触发告警发生：{payload_dict}")
            send_manual_alert_email(position=address, first_data=first_data)
        else:
            logger.info(f"手动触发告警解除：{payload_dict}")
            send_manual_alert_clearance_email(position=address, first_data=first_data)

    topic_handlers[MANUAL_ALARM_MQTT_TOPIC] = handle_manual_alert

    # 注册自动告警发生操作函数
    def handle_auto_alert(payload_dict):
        print(payload_dict)

    topic_handlers[AUTOMATIC_ALARM_MQTT_TOPIC] = handle_auto_alert

    # 默认操作函数，处理数据上报topic
    def handle_default(payload_dict, topic, payload):
        # 在这里解析mqtt上报过来的数据
        logger.info(f"esp32上报数据：{payload_dict}")
        # 数据预处理
        new_payload_dict = preprocess_data(payload_dict)
        logger.info(f"esp32上报数据预处理后：{new_payload_dict}")

        time_str = new_payload_dict['report_time']

        # 将时间字符串转换为 datetime 对象
        report_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        # 创建一个 SensorData 对象并设置 report_time 字段
        # 创建 SensorData 对象并保存到数据库
        # 如果传感器没有上报陀螺仪和加速度的数据就不用判断了
        if new_payload_dict.get('gx') is not None and new_payload_dict.get('X') is not None:
            if gyro_is_fallen(new_payload_dict) & accel_is_fallen(new_payload_dict):
                logger.error("通过计算加速度和陀螺仪判断跌倒，发送告警邮件")
                send_automatic_monitoring_alert_email(position=address, **new_payload_dict)

        lat, lng = get_coordinates(address)
        print(lat, lng)
        data = SensorData(report_time=report_time,
                          latitude=lat,
                          longitude=lng,
                          address=address,
                          temperature=new_payload_dict['temp'],
                          environment_temperature=new_payload_dict['environment_temperature'],
                          blood_oxygen=new_payload_dict['sop2'],
                          heart_rate=new_payload_dict['bmp'],
                          humidity=new_payload_dict['humidity'],
                          acceleration_x=new_payload_dict['X'],
                          acceleration_y=new_payload_dict['Y'],
                          acceleration_z=new_payload_dict['Z'],
                          topic=topic, payload=payload)
        db.session.add(data)
        db.session.commit()
        logger.info(f"数据保存成功")

    @mqtt_client.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info('连接mqtt服务器成功')
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
                logger.info(f"这个topic有操作函数{topic}")
                topic_handlers[topic](payload_dict)
            else:
                # 如果没有与当前topic关联的操作函数，则使用默认操作函数处理数据
                logger.info(f"这个topic没有操作函数{topic}")
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
