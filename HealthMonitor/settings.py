# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：bluelog
# Name:settings.py
# Description:
# Author:ChenQiancheng
# Date:2023/10/3  16:27
# --------------------------------------------------------------------------
import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'
    MAIL_SERVER = "smtp.qq.com"
    MAIL_USERNAME = "980938541@qq.com"
    MAIL_PASSWORD = "bhtjicjvwgflbcec"
    # MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    # MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    # MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = '980938541@qq.com'
    # 发邮件超时时间
    MAIL_TIMEOUT = 30

    BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')
    BLUELOG_POST_PER_PAGE = 10
    BLUELOG_MANAGE_POST_PER_PAGE = 15
    BLUELOG_COMMENT_PER_PAGE = 15
    # ('theme name', 'display name')
    BLUELOG_THEMES = {'perfect_blue': 'Perfect Blue', 'black_swan': 'Black Swan'}
    BLUELOG_SLOW_QUERY_THRESHOLD = 1

    BLUELOG_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    BLUELOG_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

    # mqtt配置
    # MQTT_BROKER_URL = 'broker.emqx.io'
    MQTT_BROKER_URL = '39.101.74.115'
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = ''
    MQTT_PASSWORD = ''
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = False
    MQTT_CLIENT_ID = "esp32"


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
