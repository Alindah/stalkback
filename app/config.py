import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SEND_FILE_MAX_AGE_DEFAULT = -1
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A poorly-kept secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AVATAR_SAVE_PATH = os.environ.get('AVATAR_SAVE_PATH') or "./app/data/user/avatars"
    AVATAR_UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
    AVATAR_MAX_SIZE = 1024 * 1024