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
    return render_template('url.html', url=url_record)


@app.get("/urls>")
def get_all_urls():
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            "SELECT * FROM urls ORDER BY urls.id;"
            )
        urls = curs.fetchall()
    return render_template('urls.html', urls=urls)


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
