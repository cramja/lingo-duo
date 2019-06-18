import json
import logging

from os import environ
import argparse
from flask import Flask, g, redirect, request, Response, render_template, flash, get_flashed_messages, Session, session, jsonify
from flask_oidc import OpenIDConnect
import requests
import pickle
from uuid import uuid4
import random

from lib import duolingo, helpers
from lib.viewmodel import TableTemplate, ColumnTemplate, Table

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

app = Flask(__name__)
app.config.update(helpers.get_config())


def require_login(fn):
    def _login(*args, **kwargs):
        if 'duo' not in session:
            return redirect("/login")
        else:
            fn(*args, **kwargs)

    return _login


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/words')
def words():
    duo = pickle.loads(session['duo'])
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
def gender():
    duo = pickle.loads(session['duo'])
    # vocab = duo.get_vocabulary()
    return render_template("gender.html", callback_url=request.host_url + "gender.json")


@app.route('/gender.json')
def gender_json():
    duo = pickle.loads(session['duo'])
    vocab = duo.get_vocabulary()
    # select 10 words which have a gender
    words = []
    while len(words) < 10:
        word = vocab[random.randint(0,len(vocab))]
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
    session['duo'] = pickle.dumps(duo)
    session['username'] = duo.username
    return redirect("/")


@app.route('/logout')
def logout():
    session.pop('duo', None)
    session.pop('username', None)
    return redirect("/login")


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
