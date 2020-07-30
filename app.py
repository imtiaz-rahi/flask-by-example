import operator
import os
import re
from collections import Counter

import json
import nltk
import requests
from rq import Queue
from rq.job import Job
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from requests.models import Response
from stop_words import STOPS
from worker import redis_conn


load_dotenv()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
queue = Queue(connection=redis_conn)

from models import Result


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


def handle_post(url: str):
    """Get site source parsed and store data in DB"""
    errors = []
    try:
        rs = requests.get(url)
    except requests.exceptions.RequestException as ex:
        errors.append('Unable to get URL. Make sure it exists.\n' + ex)
        return {"errors": errors}

    results, raw_count, non_stop_count = process_site_text(rs)
    try:
        result_obj = Result(url=url, result_all=raw_count, result_no_stop_words=non_stop_count)
        db.session.add(result_obj)
        db.session.commit()
        return result_obj.id
    except:
        errors.append('Unable to add item into database.')
        return {"errors": errors}


@app.route("/results/<job_key>", methods=["GET"])
def get_results(job_key: str):
    job = Job(job_key, connection=redis_conn)
    if not job.is_finished:
        return "Nay!", 202

    obj: Result = Result.query.filter_by(id=job.result).first()
    results = sorted(obj.result_no_stop_words.items(),
                     key=operator.itemgetter(1),
                     reverse=True)[:10]
    return jsonify(results)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def get_counts():
    data = json.loads(request.data.decode())
    url = data['url']
    if not url[:8].startswith(("https://", "http://")):
        url = "https://" + url
    job = queue.enqueue_call(func=handle_post, args=(url,), ttl=5000)
    print(job.get_id())
    return job.get_id()


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run()
