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
import validators
from urllib.parse import urlparse, urlunparse
from page_analyzer import db_manager
from page_analyzer import parser


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


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
    # check if the URL already exist in DB
    url_added = db_manager.get_url_by_name(url_new)
    if url_added:
        url_added_id = url_added.id
        flash('Страница уже существует', 'warning')
    # write new URL to DB
    else:
        url_added_new = db_manager.insert_url_to_db(url_new)
        url_added_id = url_added_new.id
        flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url_aftr_add', id=url_added_id))


@app.get("/urls/<int:id>")
def get_url_aftr_add(id):
    # get record from DB by URL id
    url_record = db_manager.get_url_by_id(id)
    # get data from DB checks table by URL id
    checks = db_manager.get_url_checks_data(id)
    return render_template('url.html', url=url_record, checks=checks)


@app.get("/urls")
def get_all_urls():
    urls = db_manager.get_all_urls()
    return render_template('urls.html', urls=urls)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    url = db_manager.get_url_by_id(id)
    content = parser.get_content(url.name)
    if not content:
        flash('Произошла ошибка при проверке', 'warning')
    else:
        db_manager.insert_checks_data(id, content)
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url_aftr_add', id=id))


# function for getting connection with DataBase
def connect_db():
    DATABASE_URL = os.getenv('DATABASE_URL')
    try:
        connection = psycopg2.connect(DATABASE_URL)
        return connection
    except Exception:
        print('Connection to the database failed')


# function for validate URL
def validate(url):
    if not validators.url(url):
        return 'Некорректный URL'
    elif len(url) > 255:
        return 'Некорректный URL'


# function for URL normalization
def normalize(url):
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    return urlunparse([scheme, netloc, '', '', '', ''])
