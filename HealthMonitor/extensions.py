# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：bluelog
# Name:extensions.py
# Description: 存储扩展实例化等操作
# Author:ChenQiancheng
# Date:2023/10/3  16:05
# --------------------------------------------------------------------------
# from flask_bootstrap import Bootstrap4
import datetime
import redis
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mqtt import Mqtt
# from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)
db = SQLAlchemy()
moment = Moment()
mqtt_client = Mqtt(mqtt_logging=True)
# ckeditor = CKEditor()
mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()
