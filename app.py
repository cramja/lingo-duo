import json
import logging

from os import environ
import argparse
from flask import Flask, g, redirect, request, Response, render_template, flash, get_flashed_messages, Session, session, \
    jsonify, url_for
from functools import wraps
import requests
import pickle
from uuid import uuid4
import random

from lib import duolingo, helpers
from lib.storage import SessionStorage
from lib.viewmodel import TableTemplate, ColumnTemplate, Table

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

app = Flask(__name__)
app.config.update(helpers.get_config())
storage = SessionStorage()


def require_login(fn):
    @wraps(fn)
    def _login(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for(get_login.__name__))
        else:
            return fn(*args, **kwargs)

    return _login


def _get_duo():
    id = session.get("id", None)
    state = storage.get_session(id)
    if state is None:
        raise Exception("session not found, please log in")
    return pickle.loads(state)


@app.route('/')
def get_index():
    return render_template("index.html")


@app.route('/words')
@require_login
def get_words():
    duo = _get_duo()
    vocab = duo.get_vocabulary()
    tt = TableTemplate(
        [
            ColumnTemplate("word_string"),
            ColumnTemplate("pos"),
            ColumnTemplate("gender")
        ]
    )

    return render_template("words.html", table=Table(tt, vocab))


@app.route('/gender')
@require_login
def get_gender():
    return render_template(
        "gender.html",
        callback_url=url_for(get_gender_json.__name__)
    )


@app.route('/gender.json')
def get_gender_json():
    duo = _get_duo()
    vocab = duo.get_vocabulary()
    # select 10 words which have a gender
    words = []
    while len(words) < 10:
        word = vocab[random.randint(0, len(vocab))]
        if word['gender'] is not None:
            words.append({
                "word": word['word_string'],
                "gender": word['gender'],
            })
    return jsonify(words)


@app.route('/login', methods=['GET'])
def get_login():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def post_login():
    duo = duolingo.Duo(
        request.form['username'],
        request.form['password'],
    )
    session['id'] = duo.username
    storage.put_session(duo.username, pickle.dumps(duo))
    return redirect(url_for(get_index.__name__))


@app.route('/logout')
def logout():
    if 'id' in session:
        _get_duo().logout()
        storage.remove_session(session['id'])
        session.pop('id', None)

    return redirect(url_for(get_login.__name__))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the web app.')
    parser.add_argument('--port',
                        type=int,
                        nargs='?',
                        default=8080,
                        help='(int) port number. Defaults to 8080.')
    parser.add_argument('--host',
                        type=str,
                        nargs='?',
                        default="localhost",
                        help='(str) host. Defaults to localhost.')
    parser.add_argument('--debug',
                        action='store_const',
                        const=True,
                        default=False,
                        help='() enable debug mode.')

    args = parser.parse_args()

    app.run(port=args.port, host=args.host, debug=args.debug)
