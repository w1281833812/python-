from info.models import User
from info.modules.home import home_blu
from flask import render_template, current_app, session


# 2.使用蓝图来装饰路由
@home_blu.route('/')
def index():
    # 判断用户是否登录
    user_id = session.get("user_id")
    user = None
    if user_id:
        # 根据user_id查询用户模型
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)

    user = user.to_dict() if user else None
    # 将用户登录信息传到模板中
    return render_template("index.html", user=user)


# 设置图标
@home_blu.route('/favicon.ico')
def favicon():
    # send_static_file用于返回静态文件
    return current_app.send_static_file("news/favicon.ico")
