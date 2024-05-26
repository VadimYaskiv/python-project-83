from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import NamedTupleCursor
import datetime
import validators
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')



try:
    connection = psycopg2.connect(DATABASE_URL)
except Exception:
    print('Connection to the database failed')


@app.route("/")
def index():
    return render_template('index.html')

@app.post("/urls")
def add_url():
    # get new URL from html form
    url_new = request.form.to_dict()['url']
    
    # check if new URL is correct
    valid_err = validate(url_new)
    if valid_err:
        flash(valid_err, 'danger')
        return render_template('index.html', url=url_new), 422
    
    # normalize new URL for DB
    url_new = normalize(url_new)

    # write new URL to DB
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            "SELECT * FROM urls WHERE name=%s;",(url_new,)
            )
        url_added = curs.fetchone()
        if url_added:
            flash('Страница уже существует', 'warning')
            return redirect(url_for('index'))
        curs.execute(
            'INSERT INTO urls(name, created_at) VALUES (%s, %s);', (url_new, datetime.datetime.now())
        )
        connection.commit()
        curs.execute(
            "SELECT * FROM urls WHERE name=%s;",(url_new,)
            )
        url_added = curs.fetchone()
        url_added_id = url_added.id
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url_aftr_add', id=url_added_id))


@app.get("/urls/<int:id>")
def get_url_aftr_add(id):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            "SELECT * FROM urls WHERE id=%s;",(id,)
            )
        url_record = curs.fetchone()
        curs.execute(
            "SELECT * FROM urls_checks WHERE url_id=%s;", (id, )
        )
        checks = curs.fetchall()
    return render_template('url.html', url=url_record, checks=checks)


@app.get("/urls>")
def get_all_urls():
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''
            SELECT DISTINCT ON (u.id)
            u.id, u.name, uch.created_at, uch.response_code
            FROM urls AS u
            LEFT JOIN urls_checks as uch ON u.id = uch.url_id
            ORDER BY u.id DESC, uch.id DESC;
            '''
            )
        urls = curs.fetchall()
    return render_template('urls.html', urls=urls)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            "SELECT * FROM urls WHERE id=%s;",(id,)
            )
        url = curs.fetchone()
        content = get_content(url.name)
        if not content:
            flash('Произошла ошибка при проверке', 'danger')
        else:
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
            flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url_aftr_add', id=id))



# function for getting data from site for urls_checks db table
def get_content(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        return False
    
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.find('h1')
    title = soup.find('title')
    description = soup.find('meta', attrs={'name': 'description'})

    site_content = {
        'response_code': response.status_code,
        'h1': h1.get_text() if h1 else '',
        'title': title.get_text() if title else '',
        'description': description['content'] if description else ''
        }
    return site_content


# function for validate URL
def validate(url):   
    if not validators.url(url):
        return 'Введите корректный URL'
    elif len(url) > 255:
        return 'Введите URL, не превышающий 255 символов'


# function for URL normalization
def normalize(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    return urlunparse([scheme, netloc, '', '','',''])
