from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import DevelopConfig

app = Flask(__name__)
# 根据配置类来加载应用配置
app.config.from_object(DevelopConfig)
# 创建数据库连接对象
db = SQLAlchemy(app)
# 创建redis连接对象
sr = StrictRedis(host=DevelopConfig.REDIS_HOST, port=DevelopConfig.REDIS_PORT)
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