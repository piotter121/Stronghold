# -*- coding: utf-8 -*-
# wszystkie importy
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# konfiguracja
DATABASE = 'database/Stronghold.db'
SECRET_KEY = 'development.key'
SERVER_MAIL = 'pyskp@ee.pw.edu.pl'
SERVER_PASS = 'pyskp12345'

# tworzenie aplikacji
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
