from datetime import timedelta
from redis import StrictRedis


class Config:  # 自定义配置类
    DEBUG = True  # 开启调试模式
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/info16"  # mysql连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库变化
    REDIS_HOST = "127.0.0.1"  # redis的ip
    REDIS_PORT = 6379  # redis的端口
    SESSION_TYPE = "redis"  # session存储的数据库类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置session存储使用的redis连接对象
    SESSION_USE_SIGNER = True  # 对cookie中保存的sessionid进行加密(需要使用app的秘钥)
    SECRET_KEY = "DxY3z7jndzYaiY1ndZh+OJOv800zHpRZiWwwNBjC5PAQ1IEMMcWqiyQ8xn2lviMg"  # 应用秘钥
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 设置session存储时间(session默认会进行持久化)


class DevelopConfig(Config):  # 定义开发环境的配置
    DEBUG = True


class ProductConfig(Config):  # 定义生产环境的配置
    DEBUG = False