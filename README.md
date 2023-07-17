# 使用 Flask + Flask RESTful 快速搭建 API 服务

[toc]



## 1. 简介

[`Flask`](https://flask.palletsprojects.com/en/latest/) 是 Python 社区中开发 Web 应用最火热的框架之一，不同于 `Django` 陡峭的学习曲线，个人感觉 Flask 非常好上手，且社区生态丰富，有很多成熟的扩展可以拿来直接安装使用。 Flask 框架自身集成了基于 `Jinja` 的模板语言，使其可以完成前后端的所有开发，但现在大部分的 Web 应用都是前后端分离，所以本文将使用 [`Flask RESTful`](https://flask-restful.readthedocs.io/en/latest/) 扩展实现一个纯后端的 API 服务。 

### 你会学到什么

通过本文可以学习到以下内容：

- 使用 `Flask` + `Flask RESTful` 搭建 API 应用并使用 `Blueprint`(蓝图) 管理 API；
- 使用 [`Flask-SQLAlchemy`](https://flask-sqlalchemy.palletsprojects.com/en/latest/quickstart/) 扩展实现 ORM 操作 MySQL 数据库；
- 基于` JWT` 验证实现注册、登录以及登出接口；
- 实现一个最基本的列表获取接口；
- 解决跨域问题；
- 使用 Docker 部署该应用。

在正式开始之前，请确保你已经安装了 Python，并且对 Python 有一定了解。

### 依赖模块

* [Flask](https://flask.palletsprojects.com/en/latest/)：Flask 是一个轻量级[WSGI](https://wsgi.readthedocs.io/) Web 应用程序框架。它旨在让入门变得快速、简单，并且能够扩展到复杂的应用程序。它最初是[Werkzeug](https://werkzeug.palletsprojects.com/) 和[Jinja](https://jinja.palletsprojects.com/)的简单包装，现已成为最流行的 Python Web 应用程序框架之一。
* [Flask-RESTful](https://flask-restful.readthedocs.io/en/latest/)：是Flask的扩展，它增加了对快速构建REST API的支持。
* [python-dotenv](https://saurabh-kumar.com/python-dotenv/)：从 `.env` 文件中读取键值对，并将其设置为环境变量。
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/latest/quickstart/)：对象关系映射 (ORM) 库。
* [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)：处理 Flask 应用程序的 SQLAlchemy 数据库迁移的扩展。数据库操作可通过 Flask 命令行界面进行。
* [PyMySQL](https://pymysql.readthedocs.io/en/latest/)：一个纯Python写的MySQL客户端库。
* [flask-jwt-extended](https://flask-jwt-extended.readthedocs.io/en/stable/)：向 Flask 添加了对使用 JSON Web Tokens (JWT) 来保护路由的支持，而且还内置了许多有用的（可选的）功能，使使用JSON Web Tokens变得更容易。
* [flask-cors](https://flask-cors.readthedocs.io/en/latest/)：用于处理跨源资源共享（CORS）的Flask扩展，使跨源AJAX成为可能。



## 2. 初始化项目

### 新建项目 & 创建虚拟环境

首先我们新建一个空文件夹，作为项目的根目录。进入到项目根目录后创建一个虚拟环境：

```bash
# 创建项目目录并进入
$ mkdir Flask-RESTful-SQLAlchemy-Migrate && cd Flask-RESTful-SQLAlchemy-Migrate
# 使用pyenv设置项目使用的Python版本
$ pyenv local 3.9.17
# 使用poetry初始化pyproject.toml文件
$ poetry init
# 激活虚拟环境
$ poetry shell
```

### 安装模块

安装 `Flask`、`Flask RESTful` 以及 [`python-dotenv`](https://saurabh-kumar.com/python-dotenv/)，最后一个包用来获取我们在项目中定义的环境变量。

```bash
$ poetry add Flask flask-restful python-dotenv
```

注意：

* 如果该`flask run`命令检测到 `dotenv` 文件（即`.env`文件）但未安装 `python-dotenv`模块，则会显示一条消息。

  ```bash
  $ flask run
   * Tip: There are .env files present. Do "pip install python-dotenv" to use them.
  ```

* 即使安装了 python-dotenv，你也可以通过设置`FLASK_SKIP_DOTENV`环境变量来告诉 [Flask 不要加载 dotenv 文件](https://flask.palletsprojects.com/en/latest/cli/#disable-dotenv)。

  ```bash
  $ export FLASK_SKIP_DOTENV=1
  $ flask run
  ```

### 简单接口的实现

按照惯例，我们先简单实现一个接口，验证下我们最基础的包是否安装完成。 首先在项目根目录下新建一个 `app` 文件夹，在 `app` 下新建一个 `__init__.py` 文件，在这个文件中，我们定义一个测试用的接口。

```python
from flask import Flask
from flask_restful import Resource, Api

# 初始化一个 Flask 应用实例
app = Flask(__name__)
# 初始化一个 flask_restful 实例
api = Api(app)


# 继承自抽象的RESTful资源类
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


# 注册路由
api.add_resource(HelloWorld, '/')
```

我们先引入了 `Flask` 和 `flask_restful` 中的 `Resource` 和 `Api`，然后我们使用 `Flask()` 初始化一个 Flask 应用实例赋值给 `app`，传入的 `__name__` 则是模块名 `"app"`，然后再使用 `Api(app)` 初始化一个 flask_restful 实例赋值给 `api`。 接下来我们定义了 `HelloWorld` 这个类，它继承于 `Resource` 类。这个类中定义一个名为 `get` 的函数，它返回一个固定的 JSON 为`{'hello': 'world'}`。

最后我们使用 `api.add_resource(HelloWorld, '/')` 去注册接口，并指定了访问路由，当访问的接口路径为 `"/"` 且请求方式为 `GET` 时，就会调用该类中定义好的 `get()` 函数处理。 你可能已经猜到了，在以 `Resource` 类为基类的派生类中，就是我们定义不同 HTTP 请求方式的地方，所以在这个类中，你还可以定义 `post`，`put`，`delete` 等函数。 接下来，我们在项目根目录中新建一个 `run.py` 文件：

```python
from app import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
```

这是一个启动文件，你可以直接在控制台中使用 `python run.py` 执行，或是和我一样，在项目根目录下新建一个 `.env` 文件用来存放环境变量：

```python
FLASK_ENV=development 	# 当前环境
FLASK_DEBUG=True 				# 开启 debug mode
FLASK_APP=run.py 				# flask项目入口文件
```

上面这些环境变量的命名方式都是 Flask 规定的，这样指定环境变量的好处就是我们可以通过控制台执行 `flask run` 命令来启动服务。 需要注意的是，如果你通过 `flask run` 命令来启动服务，那么 Flask 的配置会默认以环境变量为准，并且会忽略 `run.py` 中的配置项。 现在我们启动项目后，看到以下信息就说明服务启动成功了。

```bash
# 运行开发服务器
$ flask run
```

> - Serving Flask app 'run.py'
> - Debug mode: on
> - Running on [http://127.0.0.1:5000](https://link.juejin.cn?target=http%3A%2F%2F127.0.0.1%3A5000) Press CTRL+C to quit
> - Restarting with stat
> - Debugger is active!
> - Debugger PIN: xxx-xxx-xxx

现在你可以直接使用浏览器访问 `http://127.0.0.1:5000/` 或使用 Apifox 等接口调试工具来进行测试，看看是否会得到返回的 `{'hello': 'world'}` JSON 字符串。



## 3. 连接数据库

### 使用docker创建MySQL

```bash
# 创建/data目录以便把mysql容器的数据映射到宿主机
$ mkdir /data

# 从dockerHub上拉取官方 Mysql 5.7 镜像并启动为容器
$ docker run -d -it -v /data/mysql:/var/lib/mysql --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=my_db mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

### 安装模块

要连接数据库，需要先安装 `Flask-SQLAlchemy` 、[`Flask-Migrate`](https://flask-migrate.readthedocs.io/en/latest/) 和 [`PyMySQL`](https://pymysql.readthedocs.io/en/latest/) 这三个扩展包，Flask-SQLAlchemy 用来连接并操作数据库，Flask-Migrate 是一个数据库迁移插件，用来同步数据库的更改。最后因为我们要连接的是 MySQL 数据库，所以需要安装一个 pymysql 包。

```bash
$ poetry add Flask-SQLAlchemy Flask-Migrate PyMySQL
```

### 完善项目目录结构

接下来我们修改一下我们项目的目录结构，让我们项目的可扩展性更强。

```bash
├── .python-version  			# pyenv设置项目使用的Python版本
├── .venv/					 			# poetry创建的虚拟环境
├── app/
│   └── api/ 							# api 接口模块
│       └── __init__.py 	# 注册以及生成蓝图
│       └── common/ 			# 公共方法
│       └── models/ 			# 模型
│       └── resources/ 		# 接口
│       └── schema/ 			# 校验
│   └── __init__.py 			# 整个应用的初始化
│   └── config.py 				# 配置项
│   └── manage.py 				# 数据库迁移工具管理
├── .env 									# 环境变量
└── run.py 								# 入口文件
```

这样修改我们的项目结构，可以让我们配合 Flask 提供的 Blueprint （蓝图） 对接口进行模块化管理和开发，有助于提高我们项目的可扩展性和可维护性。 

### 配置数据库连接

接下来我们先配置数据库连接，首先你要确保你有可用的 MySQL 数据库，然后在 `/app/config.py` 中添加如下代码：

```python
import os

# 数据库相关配置
# 建议在本地根目录下新建 .env 文件维护敏感信息配置项更安全 
# 用户名
USERNAME = os.getenv('MYSQL_USER_NAME')
# 密码
PASSWORD = os.getenv('MYSQL_USER_PASSWORD')
# 地址
HOSTNAME = os.getenv('MYSQL_HOSTNAME')
# 端口
PORT = os.getenv('MYSQL_PORT')
# 数据库名称
DATABASE = os.getenv('MYSQL_DATABASE_NAME')

# 固定格式 不用改
DIALECT = 'mysql'
DRIVER = 'pymysql'


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = ''


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
```

然后我们在 `.env` 文件中新增下面的环境变量：

```python
# ...
SECRET_KEY=b'#q)\\x00\xd6\x9f<iBQ\xd7;,\xe2E' 		# flask扩展密钥
MYSQL_USER_NAME=root									 						# MySQL用户
MYSQL_USER_PASSWORD=root						 							# MySQL密码
MYSQL_HOSTNAME=192.168.56.56				 							# MySQL主机地址
MYSQL_PORT=3306							         							# MySQL端口号
MYSQL_DATABASE_NAME=my_db											    # MySQL的数据库名
```

### 初始化数据库迁移工具

在 `/app/manage.py` 文件中，初始化数据库迁移工具：

```python
from flask_migrate import Migrate

# 初始化数据库迁移工具
migrate = Migrate()
```

### 修改应用初始化文件

接下来我们修改 `/app/__init__.py` 文件：

```python
import os

from flask import Flask

from .config import config
from .api.models import db
from .api import api_blueprint
from .manage import migrate


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

    return app


# 初始化项目
app = create_app(os.getenv('FLASK_ENV', 'development'))
```

现在还缺少一个 `db` 和一个 `api_blueprint` 变量，我们先把 `db` 补上。

### 初始化ORM工具

我们在 `/app/api/models` 下新建一个 `__init__.py` 文件，在里面初始化 Flask-SQLAlchemy 扩展：

```python
from flask_sqlalchemy import SQLAlchemy

# 初始化 Flask-SQLAlchemy
db = SQLAlchemy()
```



## 4. 规划 & 定义 & 创建 蓝图

### 创建名为api的蓝图

接下来我们补充 `api_blueprint` 。 在上一节的初始化中，我们写了一个 `HelloWorld` 类并注册到 `/` 路由上，在实际开发中，我们并不会这么做，而是将业务接口拆分模块，比如 `/api/xxx`，所以现在我们需要创建一个 `api` 蓝图来统一管理，在 `/app/api/__init__.py` 文件中写入以下代码：

```python
from flask import Blueprint
from flask_restful import Api

# 新建一个蓝图
api_blueprint = Blueprint('api', __name__, url_prefix="/api")
# 初始化这个蓝图
api = Api(api_blueprint)
```

我们先使用 Flask 中的 `Blueprint` 新建一个蓝图，将前缀设置为 `/api`，然后我们使用 flask_restful 中的 `Api()` 初始化这个蓝图，假设我们在该文件中使用 `api.add_resource(HelloWorld, '/greet')` 注册了接口，那么只需要通过 `/api/greet` 进行调用即可。



## 5. 创建ORM模型并更新数据库

### 创建user模型

这一节我们创建 `User` 模型，并且利用 ORM 生成对应的数据库表，首先在 `/app/api/models` 下新建一个 `user.py`，我们在这个文件中定义 `User` 表：

```python
from ..models import db
from datetime import datetime


class UserModel(db.Model):
    """
    用户表
    """
    __tablename__ = 'user'

    # 主键 id
    id = db.Column(db.Integer(), primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    # 用户名
    username = db.Column(db.String(40), nullable=False, default='', comment='用户姓名')
    # 密码
    pwd = db.Column(db.String(102), comment='密码')
    # salt
    salt = db.Column(db.String(32), comment='salt')
    # 创建时间
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, comment='创建时间')
    # 更新时间
    updated_at = db.Column(db.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 新增用户
    def add_user(self):
        db.session.add(self)
        db.session.commit()

    # 用户字典
    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # 获取密码和 salt
    def get_pwd(self):
        return {
            "pwd": self.pwd,
            "salt": self.salt,
        }

    # 按 username 查找用户
    @classmethod
    def find_by_username(cls, username):
        return db.session.execute(db.select(cls).filter_by(username=username)).first()

    # 返回所有用户
    @classmethod
    def get_all_user(cls):
        return db.session.query(cls).all()
```

我们定义了 `User` 表中一些必要的字段以及一些常用的方法，比如新增和查询。这些方法我们后面会用到。

### 显式引入ORM模型

接下来我们需要在 `/app/__init__.py` 中显式的引入该模型：

```python
# ...
from .manage import migrate
# 重要: 所有数据库模型都需要显式的在这里导入
from .api.models.user import UserModel


def create_app(config_name):
    # ...
```

### 执行数据库迁移

现在我们要在控制台执行数据库迁移工具的同步命令，来检验数据库工具是否可用：

```bash
# 第一次初始化时使用
$ flask db init			# 创建迁移存储库
# 后面每次修改数据库字段时使用。即每次数据库模型更改时,请重复migrate和upgrade命令。
$ flask db migrate	# 生成初始迁移,可以使用-m "Initial migration."来增加message
$ flask db upgrade	# 将迁移脚本描述的更改应用到您的数据库
```

我们本次需要完整的执行这三条命了。另外需要注意的是，`flask db init` 只在我们新项目第一次初始化数据库时使用，后续有表字段修改以及新增表的时候，只需要执行后面两条命令即可。现在我们打开数据库工具查看，应该已经有两个表了。 


其中 `user` 表是我们刚创建的表，而 `alembic_version` 表是 Flask-Migrate 扩展自动创建的，打开这个表，里面有且只有一个字段 `version_num`，该字段是记录你的数据库更新迁移版本号的，这个表不要随便改动，让 Flask-Migrate 自行管理就好。

注意：`flask db init`这会将迁移文件夹添加到您的应用程序中，该文件夹的内容需要与其他源文件一起添加到版本控制中。



## 6. 实现注册接口

### 实现 register 逻辑

接下来我们实现注册接口，首先在 `/app/api/resources` 下创建 `register.py` 文件，开始写注册接口的逻辑：

```python
import uuid

from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash

from ..models.user import UserModel


class Register(Resource):
    def post(self):
        # Step: 定义参数解析器
        parser = reqparse.RequestParser()
        # 参数校验包含 `username` 和 `password` 两个字段
    		# 类型都是 `string`
    		# 取参数的位置是 `json`
    		# `dest` 则表示设置了参数的别名
        # required=True 代表为必需参数。如果请求中缺少该参数，将会返回一个错误响应。
        parser.add_argument('username', type=str, location='json')
        parser.add_argument('password', type=str, dest='pwd', location='json')
        # Step: 解析请求参数,从提供的请求中解析所有参数，并将结果作为Namespace返回
        data = parser.parse_args()
        # 按 username 查找用户
        if UserModel.find_by_username(data['username']):
            return {
                'success': False,
                'message': "Repeated username!",
                'data': None,
            }, 400
        else: 
            try:
                # 生成UUID的十六进制表示的字符串
                data['salt'] = uuid.uuid4().hex
                # 将用户的密码进行 MD5 + Salt 加密
                data['pwd'] = generate_password_hash('{}{}'.format(data['salt'], data['pwd']))
                user = UserModel(**data)
                user.addUser()
                return {
                    'success': True,
                    'message': "Register succeed!",
                    'data': None,
                }, 200
            except Exception as e:
                return {
                    'success': False,
                    'message': "Error: {}".format(e),
                    'data': None,
                }, 500
```

首先我们定义了一个继承自 `Resource` 类的 `Register` 派生类，在类里面我们定义了一个 `post` 函数，然后使用 `reqparse` 定义了接口的参数校验包含 `username` 和 `password` 两个字段，类型都是 `string`，取参数的位置是 `json`，`dest` 则表示设置了参数的别名，解析参数之后只需要用 `pwd` 即可取到请求传来的 `password` 参数。

接着我们判断了传过来的用户名是否重复，如果重复了则抛出错误信息，如果没有重复，我们将用户的密码进行 MD5 + Salt 加密，最后我们在数据库里储存加密之后的密码和 Salt。同时我们对整个加密的过程进行错误捕获，以防程序执行时报错无法通知到客户端。

### 注册接口

接下来我们在 `/app/api/__init__.py` 中去注册这个接口：

```python
# ...
from .resources.register import Register

# ...
api = Api(api_blueprint)

api.add_resource(Register, '/register')
```

Flask 默认会在开发模式下开启热更新，检测到你代码修改后它会重启服务，所以我们无需重启服务，可以直接使用调试工具进行接口测试。 

### 抽离封装优化业务逻辑

再进行下一步之前，我们先优化下代码，我们上面注册接口的代码其实是有优化空间的，可以将不重要的参数校验以及重复性的 Response 内容抽离封装。 我们先抽离参数校验部分，在 `/app/api/schema` 下新建一个 `register_sha.py` 文件，把参数校验逻辑转移到该文件内：

```python
def reg_args_valid(parser):
    # 参数校验包含 `username` 和 `password` 两个字段
    # 类型都是 `string`
    # 取参数的位置是 `json`
    # `dest` 则表示设置了参数的别名
    # required=True 代表为必需参数。如果请求中缺少该参数，将会返回一个错误响应。
    parser.add_argument('username', type=str, location='json')
    parser.add_argument('password', type=str, dest='pwd', location='json')
```

然后我们在 `/app/api/common` 下新建一个 `utils.py` 文件，封装一个公共的 Response 方法：

```python
# 公共 response 方法
def res(data=None, message='OK', success=True, code=200):
    return {
        'success': success,
        'message': message,
        'data': data,
    }, code
```

最后我们修改一下 `/app/api/resources/register.py` 文件：

```python
# ...
from werkzeug.security import generate_password_hash

from ..common.utils import res
from ..models.user import UserModel
from ..schema.register_sha import reg_args_valid


class Register(Resource):
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
                data['pwd'] = generate_password_hash('{}{}'.format(data['salt'], data['pwd']))
                user = UserModel(**data)
                user.addUser()
                return res(message="Register succeed!")
            except Exception as e:
                return res(success=False, message="Error: {}".format(e), code=500)
```



## 7. 实现登录接口

### 安装模块

现在我们来实现登录接口，在开始之前，我们需要安装[ `Flask-JWT-Extended`](https://flask-jwt-extended.readthedocs.io/en/stable/) 扩展来帮助我们完成 Token 的创建以及校验等工作。

```bash
$ poetry add flask-jwt-extended
```

### 配置JWT

安装完成后我们在 `/app/config.py` 中添加以下内容：

```python
# ...
from datetime import timedelta
# ...
class Config(object):
    # ...
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLOCKLIST_TOKEN_CHECKS = ['access']
# ...
```

在 `/.env` 中添加环境变量：

```python
# ...
JWT_SECRET_KEY=b'#q)\\x00\xd6\x9f<iBQ\xd7;,\xe2E' # jwt密钥
# ...
```

在 `/app/__init__.py` 中初始化 JWT 扩展：

```python
# ...
from flask_jwt_extended import JWTManager
# ...
def create_app(config_name):
    # ...
    # 初始化 JWT
    jwt = JWTManager(app)
    return app
# ...
```

### 实现 login 逻辑

初始化扩展后，我们在 `/app/api/resources` 下新建 `login.py`，并完成登录接口的逻辑：

```python
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token
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
        user_tuple = UserModel.find_by_username(username)
        if user_tuple:  # 已注册，进行密码校验
            try:
                (user,) = user_tuple
                pwd, salt  = user.get_pwd().get('pwd'), user.get_pwd().get('salt')
                # 安全地检查给定的存储密码哈希值，该哈希值是之前使用
                valid = check_password_hash(pwd, '{}{}'.format(salt, data['pwd']))
                if valid:  # 校验通过
                    # 生成2个token 
                    response_data = generate_token(username)
                    return res(response_data)
                else:
                    return res(success=False, message='Invalid password!', code=401)
            except Exception as e:
                return res(success=False, message='Error: {}'.format(e), code=500)
        else:  # 没注册则抛出错误
            return res(success=False, message='Unregistered username!', code=400)

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
```

同样的，我们新建了一个 `Login` 类，并且定义了一个 `post` 函数表明该接口是 POST 请求。因为登录接口传入的参数和注册接口一致，所以直接引入注册接口的校验函数。解析完参数后，判断该用户是否已经注册，如果没注册则抛出错误，如果注册了则进行密码校验，校验通过了就使用扩展提供的函数新建两个 Token，其中 `access_token` 是用来鉴权的，有效期 2 小时（在 `config.py` 中配置的），而为了避免用户需要频繁的重新登录，再生成一个`refresh_token`，当`access_token` 过期后使用 `refresh_token` 来换取新的 `access_token`，当然，`refresh_token` 也有 30 天的有效期。 接下来我们再写一下换取 Token 的接口：

```python
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
# ...
class Login(Resource):
    def post(self):
        # ...

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
```

我们直接在 `Login` 类中在声明一个 `get` 函数，然后加上 `@jwt_required` 装饰器，当加上该装饰器时，JWT 扩展会为我们自动在调用此接口时做 Token 校验，它默认是只校验 `access_token` 的，在括号内传入 `refresh=True` 则表示用有效的 `refreshToken` 也可以通过校验。 

### 注册接口

接下来我们在 `/app/api/__init__.py` 中注册该接口：

```python
# ...
from .resources.register import Register
from .resources.login import Login
# ...
api.add_resource(Register, '/register')
api.add_resource(Login, '/login', '/refreshToken')
```



## 8. 实现登出接口

### 创建revoked_tokens模型

在用户退出登录后，我们要销毁 Token，接下来我们来实现这个接口。首先我们需要一个表来存放已经销毁的 Token，在 `/app/api/models` 下新建 `revoked_token.py` 文件：

```python
from ..models import db


class RevokedTokenModel(db.Model):
    """
        已过期的token表
    """

    __tablename__ = 'revoked_tokens'

    # 主键 id
    id = db.Column(db.Integer, primary_key=True)
    # jwt 唯一标识
    jti = db.Column(db.String(120))

    # token 加黑
    def add(self):
        db.session.add(self)
        db.session.commit()

    # 查询是否是加黑的 token
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
```

我们创建一个 `revoked_tokens` 表，用来存放已经销毁的 Token，并且定义一个查询的方法，用来查询 Token 是否已销毁。 

### 实现 logout 逻辑

然后我们在 `/app/api/resources` 下新建 `logout.py` 写入登出接口逻辑：

```python
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
```

在用户退出登录时，我们先获取到 Token 中的唯一标识 `jti` 然后将它加入销毁 Token 的表中。 

### 注册接口

现在我们在 `/app/api/__init__.py` 去注册该接口：

```python
# ...
from .resources.logout import Logout
# ...
api.add_resource(Logout, '/logout',)
```

### 显式引入ORM模型 & 编写钩子函数

接下来我们需要注册一个 JWT 扩展提供的钩子函数，用来校验 Token 是否在销毁列表中。在 `/app/__init__.py` 中添加以下内容：

```python
# ...
# 重要: 所有数据库模型都需要显式的在这里导入
from .api.models.user import UserModel
from .api.models.revoked_token import RevokedTokenModel


def create_app(config_name):
# ...
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
# ...
```

至此，当用户在调用我们需要鉴权的接口时，JWT 扩展还会帮我们校验是否是已经销毁的 Token。

### 执行数据库迁移

由于我们刚才新增了一张表，所以需要执行下数据库迁移扩展的更新命令再重启服务。

```bash
$ flask db migrate
$ flask db upgrade
```



## 9. 实现获取用户列表接口

### 实现 list user 逻辑

最后我们实现一个获取用户列表的接口，刚好可以测试我们的鉴权逻辑是否都实现了，在 `/app/api/resources` 下新建 `user.py` 文件：

```python
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
```

我们定义了一个 `UserService` 类，在类中定义了一个 `get` 函数，并且添加了 `@jwt_required()` 装饰器，表示该接口需要鉴权，调用该接口返回 `user` 表中所有的用户。 

### 注册接口

在 `/app/api/__init__.py` 中注册该接口：

```python
# ...
from .resources.user import UserService
# ...
api.add_resource(UserService, '/getUserList')
```

### 增加处理datetime数据的方法

我们的 `user.user_dict()` 方法中，返回了两个时间字段，因为 Python 中 `datetime` 格式不能直接放在 JSON 中返回，所以现在我们需要新写一个将 `datetime` 转换格式的方法，在 `/app/api/common/utils.py` 中新增：

```python
# 公共 response 方法
def res(data=None, message='Ok', success=True, code=200):
# ...

# datetime 转换格式
def format_datetime_to_json(datetime, format='%Y-%m-%d %H:%M:%S'):
    return datetime.strftime(format)
```

修改 `/app/api/models/user.py` 中 `dict()` 函数：

```python
#...
from ..common.utils import format_datetime_to_json


class UserModel(db.Model):
    """
    用户表
    """
    # ...
    # 用户字典
    def user_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": format_datetime_to_json(self.created_at),
            "updated_at": format_datetime_to_json(self.updated_at),
        }
    # ...
```



## 10. 解决跨域问题

现在我们完成了所有接口的开发，如果需要在浏览器环境中进行接口调用，但前后端服务又不同源的情况下，是会出现跨域问题的，所以我们需要安装[ `Flask-CORS`](https://flask-cors.readthedocs.io/en/latest/) 扩展来解决这个问题。

```bash
$ poetry add flask-cors
```

在 `/app/__init__.py` 中使用该扩展：

```python
# ...
from flask_cors import CORS
#...
def create_app(config_name):
    # ...
    # 解决跨域
    CORS(app)
    # ...
```

至此，我们通过最简单的设置 `Access-Control-Allow-Origin: *` 响应头来控制资源跨域共享。



## 11. 通过 Docker 部署

最后我们使用 Docker 将项目部署在服务器上，我这里服务器系统使用的 Linux 发行版是 Ubuntu 18.04，在部署之前你需要自己安装好 MySQL 数据库。

我们先将项目所依赖的 Python 包导出，在项目根目录下执行：

```bash
$ poetry export -f requirements.txt --output requirements.txt
```

在项目根目录下新建 `dockerfile` 文件，写入以下内容：

```dockerfile
FROM python:3.9-alpine
WORKDIR /flask_service
EXPOSE 5000
COPY . .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && apk add tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk del tzdata
ENV FLASK_DEBUG=True \
    FLASK_APP=run.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_ENV=development \
    SECRET_KEY=b'#q)\\x00\xd6\x9f<iBQ\xd7;,\xe2E' \
    JWT_SECRET_KEY=b'#q)\\x00\xd6\x9f<iBQ\xd7;,\xe2E' \
    MYSQL_USER_NAME=root \
    MYSQL_USER_PASSWORD=root \
    MYSQL_HOSTNAME=192.168.56.56 \
    MYSQL_PORT=3306 \
    MYSQL_DATABASE_NAME=my_db
RUN flask db migrate
RUN flask db upgrade
CMD ["flask", "run"]
```

因为我们是使用 Docker 容器运行服务，所以你要确保你的容器内部可以连接到数据库，否则可能会报错。

配置`.dockerignore`文件

```
__pycache__/
.venv/
venv/
.idea/
.mypy_cache/
.DS_Store
.AppleDouble
.vscode/
.git/
.env
.gitignore
.python-version
api.http
poetry.lock
pyproject.toml
README.md
```

 然后我们使用命令行终端进入项目目录，执行打包命令：

```bash
$ sudo docker build -t flask_service_image .
```

打包完成后运行容器：

```bash
$ sudo docker run -d --restart=always -p 5000:5000 flask_service_image
```

至此，我们整个开发到部署的流程就完成了，现在可以通过你服务器的 `ip:5000/xxx` 去调用接口了。



## 12. 其他

如果你使用 Git 进行代码版本管理，那么我建议将以下文件忽略：

```
*.pyc
.venv/
.env
migrations/versions/*
```

这里特别说明一下 `migrations/versions/*` 这个忽略路径。因为我们使用的数据库迁移插件是通过维护 `alembic_version` 表内的版本号来进行管理的，大多数情况下，我们都是团队协同开发，而且本地数据库与线上数据库一定是分开的，你和你的同事又是并行开发，所以肯定会导致版本号冲突，flask-migrate 扩展虽然也提供了解决冲突的 `merge` 命令，但我们发现不太好用（可能是我使用方式不对，有研究过的同学可以交流一下）。所以最后我们采用不提交版本号文件的方式，保障在上线时不会在数据库同步上花费太多时间解决冲突。



## 13. 总结

至此，我们已经使用 Flask + Flask RESTful 快速搭建了一个 API 服务，借助于 Flask 社区丰富的扩展，我们实现了 MySQL 数据库连接、注册登录等基本接口服务，并且使用 Docker 将项目成功部署在服务器上。

