from flask import current_app
from info import sr
from info.modules.home import home_blu
import logging  # python内置的日志模块 可以在控制台中显示日志, 也可以将日志写入到文件中


# 2.使用蓝图来装饰路由
@home_blu.route('/')
def index():
    # logging.error("发现了一个错误")  # 显示效果不友好
    try:
        1 / 0
    except BaseException as e:
        current_app.logger.error("发现了一个错误: %s" % e)  # 使用flask内置的日志表达形式(显示行号)
    return 'index'
