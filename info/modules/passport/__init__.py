from flask import Blueprint

# 1. 创建蓝图对象
passport_blu = Blueprint("passport", __name__, url_prefix="/passport")

# 4. 关联视图函数
from .views import *
