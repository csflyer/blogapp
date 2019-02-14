from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_script import Manager
from configs import config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
manager = Manager()


def create_app(config_name='default'):
    '''
        给定配置名称建立App的工厂函数
    :param config_name: 配置的名称
    :return: App
    '''
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 各模块初始化App
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prifix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
