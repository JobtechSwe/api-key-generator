import logging
from apikeys import settings
import psycopg2
import sys
import base64
import random
import string

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TABLE_NAME = 'apikeys'

if not settings.PG_DBNAME or not settings.PG_USER:
    log.error("You must set environment variables for PostgresSQL (i.e. "
              "PG_HOST, PG_DBNAME, PG_USER and PG_PASSWORD.)")
    sys.exit(1)

if not settings.PG_HOST:
    log.info("PG_HOST not set, assuming local socket")
    pg_conn = psycopg2.connect(dbname=settings.PG_DBNAME,
                               user=settings.PG_USER)
else:
    pg_conn = psycopg2.connect(host=settings.PG_HOST,
                               port=settings.PG_PORT,
                               dbname=settings.PG_DBNAME,
                               user=settings.PG_USER,
                               password=settings.PG_PASSWORD,
                               sslmode=settings.PG_SSLMODE)


def query(sql, args):
    cur = pg_conn.cursor()
    cur.execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return rows


def get_key_for_ticket(ticket):
    sql = f"SELECT apikey FROM {TABLE_NAME} WHERE ticket = %s"
    res = query(sql, (ticket, ))
    if res:
        return res[0][0]
    return None


def store_key(apikey, email, name, application_id=0):
    ticket = generate_ticket()

    cur = pg_conn.cursor()
    cur.execute("INSERT INTO " + TABLE_NAME +
                " (apikey, email, name, application_id, ticket)"
                " VALUES (%s, %s, %s, %s, %s)"
                " ON CONFLICT (apikey) DO UPDATE"
                " SET email = %s, name = %s,"
                " application_id = apikeys.application_id|%s, ticket = %s",
                (apikey, email, name, application_id, ticket,
                 email, name, application_id, ticket))
    pg_conn.commit()
    return ticket


def table_exists():
    cur = pg_conn.cursor()
    cur.execute("select exists(select * from information_schema.tables "
                "where table_name=%s)", (TABLE_NAME,))
    return cur.fetchone()[0]


def create_table():
    statements = (
        """
            CREATE TABLE {table} (
                apikey VARCHAR(200) NOT NULL PRIMARY KEY,
                application_id INTEGER NOT NULL,
                name VARCHAR(100),
                email VARCHAR(256) NOT NULL,
                ticket VARCHAR(32)
            )
        """.format(table=TABLE_NAME),
        """
            CREATE TABLE api_application_ids (
                application_id INTEGER PRIMARY KEY,
                application_name VARCHAR(100) NOT NULL
            )
        """,
        "CREATE INDEX {table}_apikey_idx ON {table} (apikey)".format(table=TABLE_NAME),
        "CREATE INDEX {table}_application_id_idx ON {table} (application_id)".format(table=TABLE_NAME),
        "CREATE INDEX {table}_email_idx ON {table} (email)".format(table=TABLE_NAME),
        "CREATE INDEX {table}_ticket_idx ON {table} (ticket)".format(table=TABLE_NAME),
    )
    try:
        cur = pg_conn.cursor()
        for statement in statements:
            cur.execute(statement)
        cur.close()
        pg_conn.commit()
    except (Exception, psycopg2.DatabaseError) as e:
        log.error("Failed to create database table: %s" % str(e))
        raise e


def create_api_key(seed):
    key = base64.urlsafe_b64encode(seed.encode('utf-8')).decode('utf-8').strip('= ')
    # Ensure key is not longer than 200 chars
    if len(key) > 200:
        key = key[0:200]
    return key


def generate_ticket():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))


def sanity_check():
    if not table_exists():
        create_table()
