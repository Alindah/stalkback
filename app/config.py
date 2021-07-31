import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A poorly-kept secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AVATARS_SAVE_PATH = os.environ.get('AVATARS_SAVE_PATH') or "./data/user/avatars"
    SEND_FILE_MAX_AGE_DEFAULT = -1