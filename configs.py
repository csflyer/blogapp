import os

class Config:
    pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    VALIDATE_CODE_FONT_PATH = '../static/STFANGSO.TTF'
    DEBUG = True

    MAIL_SERVER = 'smtpdm.aliyun.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'admin@csflyer.com'
    MAIL_PASSWORD = 'LiuHui5901214'
    MAIL_SUBJECT_PREFIX = 'Crazyliu Blog'
    MAIL_SENDER = 'admin@csflyer.com'


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


