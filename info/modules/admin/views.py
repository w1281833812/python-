import time
from datetime import datetime, timedelta

from flask import request, render_template, current_app, redirect, url_for, session, g

from info.common import user_login_data
from info.models import User
from info.modules.admin import admin_blu


# 后台登录
@admin_blu.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        # 判断用户是否登录
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:  # 免密码登录
            return redirect(url_for("admin.index"))

        # 渲染页面
        return render_template("admin/login.html")
    # POST处理
    username = request.form.get("username")
    password = request.form.get("password")
    if not all([username, password]):
        return render_template("admin/login.html", errmsg="用户名/密码不完整")

    # 判断该超级管理员是否存在
    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except BaseException as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="数据查询失败")

    if not user:
        return render_template("admin/login.html", errmsg="用户不存在")

    # 校验密码
    if not user.check_password(password):
        return render_template("admin/login.html", errmsg="用户名/密码错误")

    # 状态保持
    session["user_id"] = user.id
    session["is_admin"] = True

    # 跳转页面
    return redirect(url_for("admin.index"))


# 后台首页
@admin_blu.route('/index')
@user_login_data
def index():
    user = g.user
    return render_template("admin/index.html", user=user.to_dict())


# 后台退出
@admin_blu.route('/logout')
def logout():
     session.pop("user_id", None)
     session.pop("is_admin", None)
     return redirect("/")


# 用户统计
@admin_blu.route('/user_count')
def user_count():
    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 月新增人数
    mon_count = 0
    # 获取本地日期
    t = time.localtime()
    # 先构建日期字符串
    date_mon_str = "%d-%02d-01" % (t.tm_year, t.tm_mon)
    # 日期字符串可以转为日期对象
    date_mon = datetime.strptime(date_mon_str, "%Y-%m-%d")
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= date_mon).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 日新增人数
    day_count = 0
    # 先构建日期字符串
    date_day_str = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    # 日期字符串可以转为日期对象
    date_day = datetime.strptime(date_day_str, "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time >= date_day).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 获取日活跃人数(每日的登录人数)
    active_count = []
    active_time = []
    try:
        for i in range(0, 30):
            begin_date = date_day - timedelta(days=i)
            end_date = date_day + timedelta(days=1-i)
            # 查询登录时间 >= 某日0点, < 次日0点
            one_day_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date, User.last_login < end_date).count()
            active_count.append(one_day_count)
            # 将日期对象转为日期字符串
            one_day_str = begin_date.strftime("%Y-%m-%d")
            active_time.append(one_day_str)

    except BaseException as e:
        current_app.logger.error(e)

    active_time.reverse()
    active_count.reverse()
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_count": active_count,
        "active_time": active_time
    }

    return render_template("admin/user_count.html", data=data)