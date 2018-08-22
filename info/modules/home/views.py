from info import sr
from info.modules.home import home_blu


# 2.使用蓝图来装饰路由
@home_blu.route('/')
def index():
    sr.set("age", 20)
    return 'index'
