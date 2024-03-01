# -*- coding: utf-8 -*-#
# --------------------------------------------------------------------------
# ProjectName：bluelog
# Name:__init__.py.py
# Description:
# Author:ChenQiancheng
# Date:2023/10/3  16:32
# --------------------------------------------------------------------------
import os
import click
from flask import Flask
from blueprints.monitor import monitor_bp
from extensions import db, mail, moment
from settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('monitor-system')
    # 引入配置
    app.config.from_object(config[config_name])
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
    register_template_context(app)
    return app


def register_logging(app):
    pass


def register_extension(app):
    # bootstrap.init_app(app)
    db.init_app(app)
    # ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
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
