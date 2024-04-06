# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：bluelog
# Name:models.py
# Description:
# Author:ChenQiancheng
# Date:2023/10/3  16:04
# --------------------------------------------------------------------------
import time
from datetime import datetime
from HealthMonitor.extensions import db


# 定义数据模型
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_time = db.Column(db.DateTime)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    blood_oxygen = db.Column(db.Float)
    environment_temperature = db.Column(db.Float)
    heart_rate = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(256))
    topic = db.Column(db.String(256))
    payload = db.Column(db.String(256))
    acceleration_x = db.Column(db.Float)
    acceleration_y = db.Column(db.Float)
    acceleration_z = db.Column(db.Float)
    create_time = db.Column(db.Integer, default=int(time.time()))
    update_time = db.Column(db.Integer, default=int(time.time()), onupdate=int(time.time()))

    def __repr__(self):
        return f'<SensorData id={self.id} temperature={self.temperature} ' \
               f'humidity={self.humidity} heart_rate={self.heart_rate} ' \
               f'created_at={self.create_time} updated_at={self.update_time}>'
