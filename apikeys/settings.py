import os

PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT', 5432)
PG_DBNAME = os.getenv('PG_DBNAME')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_SSLMODE = os.getenv('PG_SSLMODE', 'require')

MAIL_HOST = os.getenv('MAIL_HOST')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_SENDER = os.getenv('MAIL_SENDER', 'apirequest@jobtechdev.se')