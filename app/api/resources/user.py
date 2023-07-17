from flask_restful import Resource
from flask_jwt_extended import jwt_required
from ..models.user import UserModel
from ..common.utils import res


class UserService(Resource):
    @jwt_required()  # 表示该接口需要鉴权
    def get(self):
        user_list = UserModel.get_all_user()
        result = []
        for user in user_list:
            result.append(user.user_dict())

        return res(data=result)
