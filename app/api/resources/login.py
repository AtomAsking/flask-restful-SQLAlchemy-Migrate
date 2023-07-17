from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash

from ..schema.register_sha import reg_args_valid
from ..models.user import UserModel
from ..common.utils import res


class Login(Resource):
    def post(self):
        # 初始化解析器
        parser = reqparse.RequestParser()
        # 添加请求参数校验(因为登录接口传入的参数和注册接口一致，所以直接引入注册接口的校验函数)
        reg_args_valid(parser)
        data = parser.parse_args()
        username = data['username']
        # 判断该用户是否已经注册
        user_tuple = UserModel.find_by_username(username)
        if user_tuple:  # 已注册，进行密码校验
            try:
                (user,) = user_tuple
                pwd, salt = user.get_pwd().get('pwd'), user.get_pwd().get('salt')
                # 安全地检查给定的存储密码哈希值，该哈希值是之前使用
                valid = check_password_hash(pwd, f"{salt}{data['pwd']}")
                if valid:  # 校验通过
                    # 生成 token 
                    response_data = generate_token(username)
                    return res(response_data)
                else:
                    return res(success=False, message='Invalid password!', code=401)
            except Exception as e:
                return res(success=False, message='Error: {}'.format(e), code=500)
        else:  # 没注册则抛出错误
            return res(success=False, message='Unregistered username!', code=400)

    # 使用@jwt_required()装饰器对访问进行验证,默认是只校验accessToken,refresh=True代表用有效的refreshToken也可以通过校验
    @jwt_required(refresh=True)
    def get(self):
        # access_token过期后,需要用refresh_token来换取新的token
        # 从当前请求中提取JWT中的用户身份信息。即从refresh_token中取出用户信息
        current_username = get_jwt_identity()
        # 再生成新的 token
        access_token = create_access_token(identity=current_username)
        return res(data={'accessToken': 'Bearer ' + access_token})


# 生成token
def generate_token(uid):
    # 创建一个新的accessToken
    # 用来鉴权,有效期2小时(在config.py中配置的)
    access_token = create_access_token(identity=uid)
    # 创建一个新的refreshToken
    # 为避免用户频繁的重新登录,当accessToken过期后使用refreshToken来换取新的accessToken,refreshToken有30天的有效期
    refresh_token = create_refresh_token(identity=uid)
    return {
        'accessToken': 'Bearer ' + access_token,
        'refreshToken': 'Bearer ' + refresh_token,
    }
