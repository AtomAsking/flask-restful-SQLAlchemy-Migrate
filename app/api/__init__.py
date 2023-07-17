from flask import Blueprint
from flask_restful import Api
from .resources.register import Register
from .resources.login import Login
from .resources.logout import Logout
from .resources.user import UserService

# 新建一个蓝图
api_blueprint = Blueprint('api', __name__, url_prefix="/api")
# 初始化这个蓝图
api = Api(api_blueprint)

# 注册路由
api.add_resource(Register, '/register')
api.add_resource(Login, '/login', '/refreshToken')
api.add_resource(Logout, '/logout', )
api.add_resource(UserService, '/getUserList')
