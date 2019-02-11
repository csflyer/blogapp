class Config:
    pass


class DevelopmentConfig(Config):
    pass


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
