from flask import render_template, g, redirect, abort

from info.common import user_login_data
from info.modules.user import user_blu


# 显示个人中心
@user_blu.route('/user_info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect("/")

    user = user.to_dict() if user else None
    return render_template("news/user.html", user=user)


@user_blu.route('/base_info')
@user_login_data
def base_info():
    user = g.user
    if not user:
        return abort(404)

    return render_template("news/user_base_info.html")