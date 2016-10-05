# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# email
# Update google to allow 'less secure apps': https://www.google.com/settings/security/lesssecureapps
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['admin@example.com']

# users
MTF_CSRF_ENABLED = True
SECRET_KEY = 'difficult-to-guess'

# database
R2DO2_DB_SERVER = os.environ.get('R2DO2_DB_SERVER')
R2DO2_DB_PASSWORD = os.environ.get('R2DO2_DB_PASSWORD')
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://r2do2:' + R2DO2_DB_PASSWORD + '@' + R2DO2_DB_SERVER + ':3306/r2do2'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#pagination
TASKS_PER_PAGE = 10

#whoosh
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50
