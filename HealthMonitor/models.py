# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：bluelog
# Name:models.py
# Description:
# Author:ChenQiancheng
# Date:2023/10/3  16:04
# --------------------------------------------------------------------------
from datetime import datetime
from HealthMonitor.extensions import db


# 定义数据模型
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    heart_rate = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SensorData id={self.id} temperature={self.temperature} ' \
               f'humidity={self.humidity} heart_rate={self.heart_rate} ' \
               f'created_at={self.create_time} updated_at={self.update_time}>'
