from flask import render_template, g, redirect, abort, request, jsonify, current_app

from info.common import user_login_data
from info.constants import USER_COLLECTION_MAX_NEWS
from info.models import tb_user_collection, Category
from info.modules.user import user_blu


# 显示个人中心
from info.utils.image_storage import upload_img
from info.utils.response_code import RET, error_map


@user_blu.route('/user_info')
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect("/")

    user = user.to_dict() if user else None
    return render_template("news/user.html", user=user)


# 显示/修改个人资料
@user_blu.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return abort(404)

    if request.method == "GET":
        return render_template("news/user_base_info.html", user=user)
    # POST处理
    # 获取参数
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")
    # 校验参数
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    
    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    
    # 修改模型数据
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender
    
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
    

# 显示/修改头像
@user_blu.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    user = g.user
    if not user:
        return abort(404)

    if request.method == "GET":
        return render_template("news/user_pic_info.html", user=user.to_dict())
    # POST处理
    try:
        img_bytes = request.files.get("avatar").read()
    except BaseException as e:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    
    # 上传文件
    try:
        file_name = upload_img(img_bytes)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # 修改用户的头像URL
    user.avatar_url = file_name

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_dict())


# 显示/修改密码
@user_blu.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    user = g.user
    if not user:
        return abort(404)

    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    # POST处理
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 校验旧密码是否正确
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg=error_map[RET.PWDERR])

    # 修改密码
    user.password = new_password

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 显示我的收藏
@user_blu.route('/collection')
@user_login_data
def collection():
    user = g.user
    if not user:
        return abort(404)

    page = request.args.get("p", 1)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 将当前用户的所有收藏传到模板中
    news_list = []
    total_page = 1
    try:
        pn = user.collection_news.order_by(tb_user_collection.c.create_time.desc()).paginate(page, USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        cur_page = page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "news_list": [news.to_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("news/user_collection.html", data=data)


# 显示新闻发布页面/提交发布
@user_blu.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    user = g.user
    if not user:
        return abort(404)

    if request.method == "GET":
        # 查询所有的分类, 传到模板中
        categories = []
        try:
            categories = Category.query.all()
        except BaseException as e:
            current_app.logger.error(e)

        if len(categories):
            categories.pop(0)

        return render_template("news/user_news_release.html", categories=categories)
    # POST处理