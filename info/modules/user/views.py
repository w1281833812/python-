from flask import render_template, g, redirect, abort, request, jsonify, current_app

from info import db
from info.common import user_login_data
from info.constants import USER_COLLECTION_MAX_NEWS, QINIU_DOMIN_PREFIX
from info.models import tb_user_collection, Category, News
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
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        category_id = int(category_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 创建新闻模型
    news = News()
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.content = content
    try:
        img_bytes = index_image.read()
        file_name = upload_img(img_bytes)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    news.index_image_url = QINIU_DOMIN_PREFIX + file_name
    # 设置其他属性
    news.user_id = user.id
    news.status = 1
    news.source = "个人发布"
    
    # 添加到数据库中
    db.session.add(news)
    
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 显示我发布的新闻列表
@user_blu.route('/news_list')
@user_login_data
def news_list():
    user = g.user
    if not user:
        return abort(404)

    page = request.args.get("p", 1)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 将当前用户的所有发布的新闻传到模板中
    news_list = []
    total_page = 1
    try:
        pn = user.news_list.order_by(News.create_time.desc()).paginate(page, USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        cur_page = page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "news_list": [news.to_review_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("news/user_news_list.html", data=data)


# 显示我的关注
@user_blu.route('/user_follow')
@user_login_data
def user_follow():
    user = g.user
    if not user:
        return abort(404)

    page = request.args.get("p", 1)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 将当前用户的所有的人传到模板中
    author_list = []
    total_page = 1
    try:
        pn = user.followed.paginate(page, USER_COLLECTION_MAX_NEWS)
        author_list = pn.items
        cur_page = page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "author_list": [author.to_dict() for author in author_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("news/user_follow.html", data=data)