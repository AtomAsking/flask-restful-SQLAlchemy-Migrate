import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .config import config
from .api.models import db
from .api import api_blueprint
from .manage import migrate
# 重要: 所有数据库模型都需要显式的在这里导入
from .api.models.user import UserModel
from .api.models.revoked_token import RevokedTokenModel


def create_app(config_name):
    # 初始化 Flask 项目
    app = Flask(__name__)
    # 加载配置项
    app.config.from_object(config[config_name])
    # 初始化数据库ORM
    db.init_app(app)
    # 初始化数据库ORM迁移插件
    migrate.init_app(app, db)
    # 注册蓝图
    app.register_blueprint(api_blueprint)
    # 解决跨域
    CORS(app)
    # 初始化 JWT
    jwt = JWTManager(app)
    # 注册 JWT 钩子
    register_jwt_hooks(jwt)
    return app


def register_jwt_hooks(jwt):
    """注册 JWT 钩子,用于检查 token 是否在黑名单中。
    当用户在调用我们需要鉴权的接口( @jwt_required )时，JWT 扩展还会帮我们校验是否是已经销毁的 Token。
    """

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, decrypted_token):
        jti = decrypted_token['jti']
        return RevokedTokenModel.is_jti_blacklisted(jti)


# 初始化项目
app = create_app(os.getenv('FLASK_ENV', 'development'))
