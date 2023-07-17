from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt
from ..models.revoked_token import RevokedTokenModel
from ..common.utils import res


class Logout(Resource):
    # 使用@jwt_required()装饰器对访问进行验证,默认是只校验accessToken
    @jwt_required()
    def post(self):
        # 获取到 Token 中的唯一标识 `jti`
        jti = get_jwt()['jti']
        try:
            # 用户退出系统时,将 token 加入黑名单
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return res()
        except:
            return res(success=False, message='服务器繁忙！', code=500)
