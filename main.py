from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config:  # 自定义配置类
    DEBUG = True  # 开启调试模式
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/info16"  # mysql连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库变化


app = Flask(__name__)
# 根据配置类来加载应用配置
app.config.from_object(Config)
# 创建数据库连接对象
db = SQLAlchemy(app)


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()