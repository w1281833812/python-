# 定义索引转换过滤器
import functools

from flask import session, current_app, g

from info.models import User


def index_convert(index):
    index_dict = {1: "first", 2: "second", 3: "third"}
    return index_dict.get(index, "")


# 查询用户登录状态
def user_login_data(f):
    @functools.wraps(f)  # 可以让闭包函数wrapper使用指定函数f的函数信息 (如函数名wrapper.__name__  文档注释__doc__)
    def wrapper(*args, **kwargs):
        # 判断用户是否登录
        user_id = session.get("user_id")
        user = None
        if user_id:
            # 根据user_id查询用户模型
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)

        g.user = user  # 让g变量记录查询出的用户数据

        # 再执行原有功能
        return f(*args, **kwargs)

    return wrapper



