# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：HealthMonitor
# Name:monitor.py
# Description:
# Author:ChenQiancheng
# Date:2024/3/1  10:53
# --------------------------------------------------------------------------
import json
import random
from HealthMonitor.extensions import mqtt_client
from flask import Blueprint, render_template, jsonify

from HealthMonitor.models import SensorData

monitor_bp = Blueprint('monitor', __name__)


@monitor_bp.route('/')
def index():
    # 在实际应用中，这里可以查询数据库或者进行其他操作来获取数据
    first_data = SensorData.query.order_by(SensorData.report_time.desc()).first()
    # return render_template('monitor/index.html', latest_data=latest_data)
    return render_template("monitor/index.html", first_data=first_data)


@monitor_bp.route('/get_data', methods=['GET'])
def get_data():
    # 在实际应用中，这里可以查询数据库或者进行其他操作来获取数据
    first_data = SensorData.query.order_by(SensorData.report_time.desc()).first()
    data_dict = {
        "environment_temperature": first_data.environment_temperature,
        "temperature": first_data.temperature,
        "blood_oxygen": first_data.blood_oxygen,
        "lat": first_data.latitude,
        "lon": first_data.longitude,
        "addr": first_data.address,
        "humidity": first_data.humidity,
        "heart_rate": first_data.heart_rate,
        "report_time": first_data.report_time,

    }
    # data = random.randint(1, 10)
    return jsonify(data_dict)


# 应用的路由和视图函数
@monitor_bp.route('/publish')
def publish():
    data = {"humidity": 48, "report_time": "2024-03-01 16:49:28", "temperature": 23, "gx": 1, "gy": 1, "gz": 1, "X": 1,
            "Y": 1, "Z": 1, "temp": 2, "bmp": 1, "spo2": 1}
    payload = json.dumps(data)
    mqtt_client.publish(topic='esp32/report/data', payload=payload)
    return "Message published"
