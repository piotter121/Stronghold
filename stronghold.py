# -*- coding: utf-8 -*-
# wszystkie importy
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# konfiguracja
DATABASE = 'Stronghold.db'
SECRET_KEY = 'development.key'
SERVER_MAIL = 'pyskp@ee.pw.edu.pl'
SERVER_PASS = 'pyskp12345'

# tworzenie aplikacji
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
@app.route('/home')
def home(loginfo=None):
	return forts(loginfo)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
