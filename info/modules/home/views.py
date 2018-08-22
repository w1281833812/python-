from info.modules.home import home_blu


# 2.使用蓝图来装饰路由
@home_blu.route('/')
def index():
    return 'index'
