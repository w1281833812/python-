from flask import current_app, abort, render_template

from info.models import News
from info.modules.news import news_blu


# 显示新闻详情
@news_blu.route('/<int:news_id>')
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
    # 将模型数据传到模板中
    return render_template("news/detail.html", news=news.to_dict())