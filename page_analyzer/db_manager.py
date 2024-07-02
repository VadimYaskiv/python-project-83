import os
import psycopg2
from psycopg2.extras import NamedTupleCursor, RealDictCursor
from dotenv import load_dotenv
import datetime


load_dotenv()


def connect_db():
    DATABASE_URL = os.getenv('DATABASE_URL')
    try:
        connection = psycopg2.connect(DATABASE_URL)
        return connection
    except Exception:
        print('Connection to the database failed')


def get_url_by_name(url_name):
    connection = connect_db()
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            "SELECT * FROM urls WHERE name=%s;", (url_name, )
        )
        url_data = curs.fetchone()
    return url_data


def insert_url_to_db(url_name):
    connection = connect_db()
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''
            INSERT INTO urls(name, created_at)
            VALUES (%s, %s);
            ''',
            (url_name, datetime.datetime.now())
        )
        connection.commit()
        curs.execute(
            "SELECT * FROM urls WHERE name=%s;", (url_name, )
        )
        url_data = curs.fetchone()
    return url_data


def get_url_by_id(id):
    connection = connect_db()
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            "SELECT * FROM urls WHERE id=%s;", (id, )
        )
        url_data = curs.fetchone()
    return url_data


def get_url_checks_data(id):
    connection = connect_db()
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''
            SELECT * FROM urls_checks WHERE url_id=%s
            ORDER BY urls_checks.id DESC;
            ''', (id, )
        )
        checks = curs.fetchall()
    return checks


def get_all_urls():
    connection = connect_db()
    with connection.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute(
            '''
            SELECT id, name FROM urls ORDER BY id DESC;
            '''
        )
        urls = curs.fetchall()
        curs.execute(
            '''
            SELECT DISTINCT ON (url_id)
            url_id, response_code, created_at
            FROM urls_checks
            ORDER BY url_id DESC;
            '''
        )
        checks = curs.fetchall()

    for url in urls:
        for check in checks:
            if url['id'] == check['url_id']:
                url['created_at'] = check['created_at']
                url['response_code'] = check['response_code']

        # curs.execute(
        #     '''
        #     SELECT DISTINCT ON (u.id)
        #     u.id, u.name, uch.created_at, uch.response_code
        #     FROM urls AS u
        #     LEFT JOIN urls_checks as uch ON u.id = uch.url_id
        #     ORDER BY u.id DESC, uch.id DESC;
        #     '''
        # )
        # urls = curs.fetchall()
    return urls


def insert_checks_data(id, content):
    connection = connect_db()
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''
            INSERT INTO urls_checks
            (url_id, response_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);
            ''',
            (
                id,
                content['response_code'],
                content['h1'],
                content['title'],
                content['description'],
                datetime.datetime.now(),
            )
        )
        connection.commit()
    return True
