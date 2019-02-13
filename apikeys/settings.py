import os

PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT', 5432)
PG_DBNAME = os.getenv('PG_DBNAME')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_SSLMODE = os.getenv('PG_SSLMODE', 'require')
