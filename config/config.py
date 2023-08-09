from pathlib import Path
import os

basedir = Path().cwd().resolve()

class Config(object):
    BASE_DIR = basedir
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False