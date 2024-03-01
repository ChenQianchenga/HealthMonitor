# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：HealthMonitor
# Name:monitor.py
# Description:
# Author:ChenQiancheng
# Date:2024/3/1  10:53
# --------------------------------------------------------------------------
from flask import Blueprint

monitor_bp = Blueprint('monitor', __name__)


@monitor_bp.route('/')
def index():
    return "hello world"
