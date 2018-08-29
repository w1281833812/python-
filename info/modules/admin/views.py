from flask import request, render_template, current_app, redirect, url_for

from info.models import User
from info.modules.admin import admin_blu


# 后台登录
@admin_blu.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
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

    # 跳转页面
    return redirect(url_for("admin.index"))


# 后台首页
@admin_blu.route('/index')
def index():
    return render_template("admin/index.html")

