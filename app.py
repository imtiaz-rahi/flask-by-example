import functools
import os
import re
import operator
import time
from collections import Counter

import nltk
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from requests.models import Response
from stop_words import STOPS


load_dotenv()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        run_time = time.perf_counter() - start_time
        print(f"{func.__name__!r} finished running in {run_time:.4f} secs")
        return value
    return wrapper_timer


def process_site_text(rs: Response):
    """Process site response (HTML) into raw text and tokenize using nltk """
    results = {}
    if not rs: return results

    # Add custom nltk data download location, if needed
    # nltk.data.path.append('./nltk-data/')
    raw = BeautifulSoup(rs.text, 'html.parser').get_text()
    text = nltk.Text(nltk.word_tokenize(raw))
    # remove punctuation, count raw words
    non_punc = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if non_punc.match(w)]
    raw_word_count = Counter(raw_words)
    non_stop_words = [w for w in raw_words if w.lower() not in STOPS]
    non_stop_words_count = Counter(non_stop_words)

    # results = sorted(non_stop_words_count.items(), key=operator.itemgetter(1), reverse=True)
    results = sorted(non_stop_words_count.items(), key=lambda x: x[1], reverse=True)
    return results, raw_word_count, non_stop_words_count


@timer
def handle_post():
    """Get site source parsed and store data in DB"""
    errors = []
    try:
        url = request.form['url']
        rs = requests.get(url)
    except requests.exceptions.RequestException as ex:
        errors.append('Unable to get URL. Make sure it exists.\n' + ex)

    results, raw_count, non_stop_count = process_site_text(rs)
    try:
        result_obj = Result(url=url, result_all=raw_count, result_no_stop_words=non_stop_count)
        db.session.add(result_obj)
        db.session.commit()
    except:
        errors.append('Unable to add item into database.')

    return errors, results


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        errors, results = handle_post()
    return render_template('index.html', errors=errors, results=results)


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run()
