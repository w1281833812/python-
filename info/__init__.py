from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config import config_dict


# 定义函数来封装应用的创建   工厂函数
def create_app(config_type):
    # 根据配置类型取出配置类
    config_class = config_dict[config_type]
    app = Flask(__name__)
    # 根据配置类来加载应用配置
    app.config.from_object(config_class)
    # 创建数据库连接对象
    db = SQLAlchemy(app)
    # 创建redis连接对象
    sr = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    # 初始化Session存储对象
    Session(app)
    # 初始化迁移器
    Migrate(app, db)

    return app