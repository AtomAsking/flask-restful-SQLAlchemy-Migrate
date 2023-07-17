import uuid

from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash

from ..common.utils import res
from ..models.user import UserModel
from ..schema.register_sha import reg_args_valid


class Register(Resource):
    """
    reqparse用于解析请求参数的工具。它提供了一种简单的方式来从请求中提取和验证参数，并可根据需要进行转换和处理。
    """
    def post(self):
        # 定义参数解析器
        parser = reqparse.RequestParser()
        reg_args_valid(parser)
        # 解析请求参数:从提供的请求中解析所有参数，并将结果作为Namespace返回
        data = parser.parse_args()
        # 按 username 查找用户
        if UserModel.find_by_username(data['username']):
            return res(success=False, message="Repeated username!", code=400)
        else:
            try:
                # 生成UUID的十六进制表示的字符串
                data['salt'] = uuid.uuid4().hex
                # 将用户的密码进行 MD5 + Salt 加密
                data['pwd'] = generate_password_hash(f"{data['salt']}{data['pwd']}")
                user = UserModel(**data)
                user.add_user()
                return res(message="Register succeed!")
            except Exception as e:
                return res(success=False, message="Error: {}".format(e), code=500)
