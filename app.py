import json
import logging

from os import environ
import argparse
from flask import Flask, g, redirect, request, Response, render_template, flash, get_flashed_messages, Session, session
from flask_oidc import OpenIDConnect
import requests
import pickle
from uuid import uuid4

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


@app.route('/index')
# @require_login
def index():
    duo = pickle.loads(session['duo'])
    vocab = duo.get_vocabulary()
    tt = TableTemplate(
        [
            ColumnTemplate("word_string"),
            ColumnTemplate("pos")
        ]
    )

    return render_template("index.html", table=Table(tt, vocab))


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
    return redirect("/index")


@app.route('/logout')
def logout():
    session.pop('duo', None)
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
