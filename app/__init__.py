from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_session import Session
from flask_moment import Moment
from configs import config

db = SQLAlchemy(use_native_unicode='utf-8')
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'global.login_err'
pagedown = PageDown()
mail = Mail()
sess = Session()
moment = Moment()


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
    mail.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)

    from .globals import global_view as global_blueprint
    app.register_blueprint(global_blueprint)

    # from .api import api as api_blueprint
    # app.register_blueprint(api_blueprint, url_prefix='/api')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint, url_prefix='/profile')

    return app
