import os
import redis
import logging


class Config:
    pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    VALIDATE_CODE_FONT_PATH = '/Users/crazyliu/Code/Py/blogapp/app/static/STFANGSO.TTF'
    DEBUG = True

    MAIL_SERVER = 'smtpdm.aliyun.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = 'Crazyliu Blog'
    MAIL_SENDER = os.environ.get('MAIL_USERNAME')
    JSON_AS_ASCII = False

    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USER_SIGNER = False
    SESSION_KEY_PREFIX = 'session:'
    SESSION_REDIS = redis.Redis(host='127.0.0.1', port='6379')

    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10
    USER_PER_PAGE = 20

    POST_ALLOW_TAGS = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']

    EMAIL_EXPIRATION = 3600
    log_file_path = '/Users/crazyliu/Code/.log'
    logging.basicConfig(filename=log_file_path, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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


