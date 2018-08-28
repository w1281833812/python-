from flask import current_app, abort, render_template, session, g, request, jsonify
from sqlalchemy.sql.functions import user

from info import db
from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, User, Comment
from info.modules.news import news_blu
from info.utils.response_code import RET, error_map


# 显示新闻详情
@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # 根据新闻id来查询该新闻模型
    news = None   # type: News
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)

    if not news:
        return abort(404)

    # 让新闻的点击量+1
    news.clicks += 1

    # 查询新闻 按照点击量的倒序排列 取前10条
    rank_list = []
    try:
        rank_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)

    rank_list = [news.to_basic_dict() for news in rank_list]

    # 查询当前用户是否收藏了该新闻
    is_collected = False
    user = g.user
    if user:
        if news in user.collection_news:  # 当执行了懒查询的关系属性和in联用时(if in / for in), 会直接执行查询, 而不需要添加all()
            is_collected = True

    # 查询该新闻的所有评论,传到模板中
    # comments = [comment.to_dict() for comment in news.comments]
    comments = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()

    # 查询当前用户是否对某条评论点过赞
    comments_list = []
    if user:
        for comment in comments:
            is_like = False
            comment_dict = comment.to_dict()
            if comment in user.like_comments:
                is_like = True
            comment_dict["is_like"] = is_like
            # 将评论字典加入列表中
            comments_list.append(comment_dict)

    # 将用户登录信息传到模板中
    user = user.to_dict() if user else None

    # 将模型数据传到模板中
    return render_template("news/detail.html", news=news.to_dict(), rank_list=rank_list, user=user, is_collected=is_collected, comments=comments_list)


# 收藏/取消收藏
@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])
    # 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 根据action执行处理(user_id和news_id建立/取消关系)
    if action == "collect":  # 收藏
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:  # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)

    # 返回json结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 评论/回复
@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_content = request.json.get("comment")
    news_id = request.json.get("news_id")
    parent_id = request.json.get("parent_id")
    # 校验参数
    if not all([comment_content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 生成评论模型
    comment = Comment()
    comment.content = comment_content
    comment.user_id = user.id
    comment.news_id = news.id
    if parent_id:
        try:
            parent_id = int(parent_id)
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
        comment.parent_id = parent_id

    # 添加到数据库中
    try:
        db.session.add(comment)
        db.session.commit()  # 虽然SQLALCHEMY_COMMIT_ON_TEARDOWN可以在请求结束后自动提交, 但是此处需要返回评论的主键id, 所以需要主动提交先生成主键
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())



# 点赞/取消点赞
@news_blu.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])
    # 获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    # 校验参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        comment_id = int(comment_id)
    except BaseException as e:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 根据action执行处理(user_id和comment_id建立/取消关系)
    if action == "add":  # 点赞
        if comment not in user.like_comments:
            user.like_comments.append(comment)
            comment.like_count += 1
    else:  # 取消点赞
        if comment in user.like_comments:
            user.like_comments.remove(comment)
            comment.like_count -= 1

    # 返回json结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])