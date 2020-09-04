import os


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'FKENFQ13O4IINF$34N$F!43N67$NFN7')


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    pass
