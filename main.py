from datetime import timedelta

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


class Config:  # 自定义配置类
    DEBUG = True  # 开启调试模式
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/info16"  # mysql连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库变化
    REDIS_HOST = "127.0.0.1"  # redis的ip
    REDIS_PORT = 6379  # redis的端口
    SESSION_TYPE = "redis"  # session存储的数据库类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置session存储使用的redis连接对象
    SESSION_USE_SIGNER = True  # 对cookie中保存的sessionid进行加密(需要使用app的秘钥)
    SECRET_KEY = "DxY3z7jndzYaiY1ndZh+OJOv800zHpRZiWwwNBjC5PAQ1IEMMcWqiyQ8xn2lviMg"  # 应用秘钥
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 设置session存储时间(session默认会进行持久化)


app = Flask(__name__)
# 根据配置类来加载应用配置
app.config.from_object(Config)
# 创建数据库连接对象
db = SQLAlchemy(app)
# 创建redis连接对象
sr = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 初始化Session存储对象
Session(app)
# 创建管理器
mgr = Manager(app)
# 初始化迁移器
Migrate(app, db)
# 添加迁移命令
mgr.add_command("mc", MigrateCommand)


@app.route('/')
def index():
    session["name"] = "zs"
    return 'index'


if __name__ == '__main__':
   mgr.run()