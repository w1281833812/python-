from flask import Blueprint

# 1. 创建蓝图对象
news_blu = Blueprint("news", __name__, url_prefix="/news")

# 4. 关联视图函数
from .views import *
