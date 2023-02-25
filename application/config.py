import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = None


class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + \
    #     os.path.join(SQLITE_DB_DIR, "blog-lite-db.sqlite3")
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://rajeshy45:af16c1a4@db4free.net:3306/blog_lite"
    DEBUG = True
    SECRET_KEY = "blog-lite-security-key"
