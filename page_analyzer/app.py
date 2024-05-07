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
    url_new = request.form.to_dict()['url']
    
    #conn = db_connect
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'INSERT INTO urls(name, created_at) VALUES (%s, %s);', (url_new, datetime.datetime.now())
        )
        curs.execute("SELECT * FROM urls;")
        all_users = curs.fetchall()
    connection.close()
    print(all_users)
    flash('url has been added', 'success')
    return redirect(url_for('index'))