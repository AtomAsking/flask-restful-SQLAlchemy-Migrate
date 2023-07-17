def reg_args_valid(parser):
    # 参数校验包含 `username` 和 `password` 两个字段
    # 类型都是 `string`
    # 取参数的位置是 `json`
    # `dest` 则表示设置了参数的别名
    # required=True 代表为必需参数。如果请求中缺少该参数，将会返回一个错误响应。
    parser.add_argument('username', type=str, location='json', required=True)
    parser.add_argument('password', type=str, dest='pwd', location='json', required=True)
