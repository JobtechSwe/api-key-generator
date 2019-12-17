import logging
import sys
import json
import base64
import hashlib
import random
import string
import psycopg2
from apikeys import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TABLE_NAME = 'apikeys'
APPLICATION_TABLE = 'available_apis'

pg_conn = None

if not settings.PG_DBNAME or not settings.PG_USER:
    log.error("You must set environment variables for PostgresSQL (i.e. "
              "PG_HOST, PG_DBNAME, PG_USER and PG_PASSWORD.). Exit!")
    sys.exit(1)


def connect_database():
    global pg_conn
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
        log.info("Connected to Host: %s:%s DB: %s User: %s" % (
            settings.PG_HOST, settings.PG_PORT, settings.PG_DBNAME,
            settings.PG_USER))


def query(sql, args):
    if not pg_conn or pg_conn.closed > 0:
        log.info("Connection to DB is closed. Connecting...")
        connect_database()
    cur = pg_conn.cursor()
    cur.execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return rows


def get_unsent_keys():
    sql = f"SELECT email, ticket FROM {TABLE_NAME} WHERE sent = 0"
    res = query(sql, ())
    if res:
        log.info("Found unsent key(s) (email, ticket): %s" % res)
    return res


def set_sent_flag(email, flag=0):
    if not pg_conn or pg_conn.closed > 0:
        log.info("Connection to DB is closed. Connecting...")
        connect_database()
    sql = f"UPDATE {TABLE_NAME} SET sent = %s WHERE email = %s"
    cur = pg_conn.cursor()
    cur.execute(sql, (flag, email,))
    pg_conn.commit()
    cur.close()
    log.debug("Set sent flag: %d for email: %s" % (flag, email))


def get_key_for_ticket(ticket):
    sql = f"SELECT apikey FROM {TABLE_NAME} WHERE ticket = %s" + \
          " AND (visited > (CURRENT_TIMESTAMP - interval '10 mins') " + \
          " OR visited IS NULL)"
    res = query(sql, (ticket,))
    if res:
        return res[0][0]
    return None


def get_keys_for_api(api_id):
    sql = f"SELECT apikey,id,application_id FROM {TABLE_NAME} WHERE api_id & %s = %s"
    res = query(sql, (api_id, api_id,))
    if res:
        return {key[0]: {"id": key[1], "app": key[2]} for key in res}
    return []


def set_visited(key, force=False):
    if key:
        sql = f"UPDATE {TABLE_NAME} SET visited = CURRENT_TIMESTAMP" + \
              " WHERE ticket = %s"
        if not force:
            sql += " AND visited is null"
    else:
        log.debug("Called set_visited() without key.")
        return

    if not pg_conn or pg_conn.closed > 0:
        log.info("Connection to DB is closed. Connecting...")
        connect_database()
    cur = pg_conn.cursor()
    cur.execute(sql, (key,))
    pg_conn.commit()
    cur.close()


def get_available_applications():
    sql = f"SELECT api_id, name, description FROM {APPLICATION_TABLE}"
    res = query(sql, ())
    if res:
        return [{'id': item[0], 'name': item[1], 'description': item[2]}
                for item in res]
    return []


def store_key(apikey, email, application_id, userinfo, api_id=0):
    ticket = generate_ticket()
    log.debug("STORING apikey %s, email %s, user %s, api_id %s"
              % (apikey, email, userinfo, api_id))

    if not pg_conn or pg_conn.closed > 0:
        log.info("Connection to DB is closed. Connecting...")
        connect_database()
    cur = pg_conn.cursor()
    cur.execute("INSERT INTO " + TABLE_NAME +
                " (apikey, email, application_id, userinfo, api_id, ticket)"
                " VALUES (%s, %s, %s, %s, %s, %s)"
                " ON CONFLICT (email) DO UPDATE"
                " SET email = %s, application_id = %s, userinfo = %s,"
                " api_id = apikeys.api_id|%s, ticket = %s, visited = null, sent = 0",
                (apikey, email, application_id, json.dumps(userinfo), api_id, ticket,
                 email, application_id, json.dumps(userinfo), api_id, ticket))
    pg_conn.commit()
    cur.close()
    return ticket


def table_exists(table):
    if not pg_conn or pg_conn.closed > 0:
        log.info("Connection to DB is closed. Connecting...")
        connect_database()
    cur = pg_conn.cursor()
    cur.execute("select exists(select * from information_schema.tables "
                "where table_name=%s)", (table,))
    return cur.fetchone()[0]


def _execute_statments(statements):
    if not pg_conn or pg_conn.closed > 0:
        log.info("Connection to DB is closed. Connecting...")
        connect_database()
    try:
        cur = pg_conn.cursor()
        for statement in statements:
            cur.execute(statement)
        pg_conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as e:
        log.error("Failed to create database table: %s" % str(e))
        raise e


def create_api_key(seed):
    sha1 = str(hashlib.sha1(seed.encode('utf-8')).digest())
    key = base64.urlsafe_b64encode(sha1.encode('utf-8')).decode('utf-8').strip('=- ')
    # Ensure key is not longer than 200 chars
    if len(key) > 200:
        key = key[0:200]
        log.info("Api-Key length was > 200. Set to 200")
    return key


def generate_ticket():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))


def sanity_check():
    if not table_exists(TABLE_NAME):
        _execute_statments(
            (
                """
                    CREATE TABLE {table} (
                        id SERIAL PRIMARY KEY,
                        apikey VARCHAR(256) NOT NULL UNIQUE,
                        api_id INTEGER NOT NULL,
                        application_id VARCHAR(256) NOT NULL,
                        userinfo JSONB,
                        email VARCHAR(256) NOT NULL UNIQUE,
                        ticket VARCHAR(32),
                        sent INTEGER NOT NULL DEFAULT 0,
                        visited TIMESTAMP WITH TIME ZONE
                    )
                """.format(table=TABLE_NAME),
                "CREATE INDEX {table}_apikey_idx ON {table} (apikey)".format(table=TABLE_NAME),
                "CREATE INDEX {table}_api_id_idx ON {table} (api_id)".format(table=TABLE_NAME),
                "CREATE INDEX {table}_email_idx ON {table} (email)".format(table=TABLE_NAME),
                "CREATE INDEX {table}_ticket_idx ON {table} (ticket)".format(table=TABLE_NAME),
            )
        )
    if not table_exists(APPLICATION_TABLE):
        _execute_statments(
            (
                """
                    CREATE TABLE {table} (
                        api_id INTEGER PRIMARY KEY,
                        name VARCHAR(30) NOT NULL,
                        description VARCHAR(200)
                    )
                """.format(table=APPLICATION_TABLE),
            )
        )
