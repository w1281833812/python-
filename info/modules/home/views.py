from info.modules.home import home_blu
from flask import render_template, current_app


# 2.使用蓝图来装饰路由
@home_blu.route('/')
def index():

    return render_template("index.html")


# 设置图标
@home_blu.route('/favicon.ico')
def favicon():
    # send_static_file用于返回静态文件
    return current_app.send_static_file("news/favicon.ico")
