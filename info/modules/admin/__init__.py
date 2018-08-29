from flask import Blueprint

# 1. 创建蓝图对象
admin_blu = Blueprint("admin", __name__, url_prefix="/admin")


# 使用蓝图的请求勾子(只要访问该蓝图注册的路由,都会被勾子拦截), 对后台访问进行控制
@admin_blu.before_request
def check_superuser():
    # 判断是否登录管理员
    is_admin = session.get("is_admin")
    # 如果没有后台登录 且不是访问后台登录页面, 则重定向到前台首页
    if not is_admin and not request.url.endswith("admin/login"):
        return redirect("/")


# 4. 关联视图函数
from .views import *
