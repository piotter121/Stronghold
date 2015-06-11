import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from pass_check import hash_password, compare_password, random_string
import time
import smtplib
import re
import io

DATABASE = 'database/Stronghold.db'
SECRET_KEY = 'development.key'
SERVER_MAIL = 'rraf@spoko.pl'
SERVER_PASS = 'Mahdi248'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

#def hex_to_rgb(value):
#    value = value.lstrip('#')
#    lv = len(value)
#    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

#def rgb_to_hex(rgb):
#    return '#%02x%02x%02x' % rgb

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
	
@app.route('/forts')
def forts(loginfo=None):
    col_cur = g.db.execute('SELECT username, color FROM users ORDER BY id DESC')
    color_tmp = [dict(username=row[0], color=row[1]) for row in col_cur.fetchall()]
    color = {}
    bgcolor = {}
    #for crl in color_tmp:
    #    c = hex_to_rgb(crl['color'])
    #    d = (c[0] + 44, c[1] + 44, c[2] + 44)
    #    if d[0] > 255:
    #        d = (255, d[1], d[2])
    #    if d[1] > 255:
    #        d = (d[0], 255, d[2])
    #    if d[2] > 255:
    #        d = (d[0], d[1], 255)
    #    color[crl['username']] = rgb_to_hex(d)
    #    d = (c[0] / 2, c[1] / 2, c[2] / 2)
    #    bgcolor[crl['username']] = rgb_to_hex(d)
    cur = g.db.execute('SELECT author, text FROM entries ORDER BY id DESC')
    entries = [dict(author=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('forts.html', entries=entries, color=color, bgcolor=bgcolor, loginfo=loginfo)
    
@app.route('/addfort', methods=['POST'])
def addfort():
    if not session.get('logged_in'):
        abort(401)
    text = request.form['text']
    if re.search(r"[<>=/\+\?\.\*\^\$\(\)\[\]\{\}\|\\]{1,}", text):
        error = "Filed 'about' contains invalid characters"
    else:
        g.db.execute('INSERT INTO entries (author, text, data) VALUES (?, ?, ?)',
                 [session['logged_user'], text, time.strftime("%c")])
        g.db.commit()
    return redirect(url_for('forts'))
    
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        session['login_count'] += 1
        cur = g.db.execute('SELECT username, password FROM users ORDER BY id DESC')
        entries = [dict(username=row[0], password=row[1]) for row in cur.fetchall()]
        length = len(entries)
        for i in range (0, length + 1):
            try:
                if entries[i]['username'] == username:
                    break
            except IndexError:
                i += 1
                break
        if session['login_count'] == 3:
            error = "Invalid login attempt. Please try later"
        elif i > length:
            error = 'Invalid username'
        else:
            if not compare_password(bytes(request.form['password']), bytes(entries[i]['password'])):
                error = 'Invalid password'
            else:
                loginfo = None
                session['logged_in'] = True
                session['logged_user'] = username
                cur = g.db.execute('SELECT ip FROM users WHERE username=?', [username])
                iplist = cur.fetchall()
                iplist = iplist[0][0]
                iplist = iplist.split("\n")
                lastip = iplist[len(iplist) - 2]
                lastip = lastip.split(" ")[0]
                currentip = request.environ['REMOTE_ADDR']
                if lastip != currentip:
                    loginfo = "You were logged from diferent ip"
                g.db.execute("UPDATE users SET ip=ip || ? || ' ' || ? || '\n' WHERE username=?", [request.environ['REMOTE_ADDR'], time.strftime("%c"), session['logged_user']])
                g.db.commit()
                return home(loginfo=loginfo)
    if 'login_count' not in session:
        session['login_count'] = 0
    return render_template('signin.html', error=error)
    
def user_exist(username):
    exist = False
    cur = g.db.execute('SELECT username FROM users ORDER BY id DESC')
    registered = [dict(username=row[0]) for row in cur.fetchall()]
    for i in range (0, len(registered)):
        if registered[i]['username'] == username:
            exist = True
            break
    return exist
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        
        if username == "":
            error = 'Empty username field'
        elif username.isalnum() == False:
            error = "Username contains illegal characters"
        elif user_exist(username) == True:
            error = "Username already exist"
        elif email == "":
            error = "Empty email field"
        elif not re.match(r"^[a-zA-Z0-9._-]+\@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$", email):
            error = "Invalid email address"
        elif password == "":
            error = "Empty password field"
        elif len(password) < 5:
            error = "Password too short. Minimum 6 characters"
        elif password != repassword:
            error = "Passwords does not match"
        else:
            g.db.execute("INSERT INTO users (username, password, email, color, ip) values (?, ?, ?, ?, ? || ' ' || ? || '\n')",
                 [username, hash_password(password), email, '#000000', request.environ['REMOTE_ADDR'], time.strftime("%c")])
            g.db.commit()
            session['logged_in'] = True
            session['logged_user'] = username
            return redirect(url_for('home'))
    return render_template('signup.html', error=error)
    
@app.route('/signout')
def signout():
    session['login_count'] = 0
    session.pop('logged_in', None)
    session.pop('logged_user', None)
    return redirect(url_for('home'))

def send_mail(msg, email_to):
    email_from = app.config['SERVER_MAIL']
    email_pass = app.config['SERVER_PASS']
    
    server = smtplib.SMTP('smtp.poczta.onet.pl:587')
    server.starttls()
    server.login(email_from, email_pass)
    server.sendmail(email_from, email_to, msg)
    server.quit()
    
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = None;
    if request.method == 'POST':
        username = request.form['username']
        cur = g.db.execute('SELECT email FROM users WHERE username=?', [username])
        email_to = cur.fetchall()
        
        try:
            email_to = email_to[0][0]
        except IndexError:
            error = "User not found"
            return render_template('forgot.html', error=error)
         
        session['secret_token'] = random_string()
        msg = """foRtReSS Support Welcome!
Rewrite this link into your browser to change your password:
   
https://volt.iem.pw.edu.pl:8000/newpass?q=%s&u=%s
""" % (session['secret_token'], username)
        send_mail(msg, email_to)
        error = "We have send you a uniqe email message. Please check your email box"
    return render_template('forgot.html', error=error)

@app.route('/newpass', methods=['GET', 'POST'])
def newpass():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['new_pass']
        re_password = request.form['re_new_pass']
        
        if password == "":
            error = "Empty password"
            return render_template('newpass.html', user=user, error=error)
        if password != re_password:
            error = "Passwords does not match"
            return render_template('newpass.html', user=user, error=error)
        g.db.execute('UPDATE users SET password=? WHERE username=?', [hash_password(password), user])
        g.db.commit()
        session['logged_in'] = False
        session['logged_user'] = ''
        session['secret_token'] = ''
        return home()
    if request.args.get('q') == session['secret_token']:
        user = request.args.get('u')
        return render_template('newpass.html', user=user)
    else:
        return home()

@app.route('/profile')
def profile(cherror=None, posinfo=None, error=None, chinfo=None):
    cur = g.db.execute('SELECT name, surname, email, color, about FROM users WHERE username=?', [session['logged_user']])
    info = [dict(name=row[0], surname=row[1], email=row[2], color=row[3], about=row[4]) for row in cur.fetchall()]
    return render_template('profile.html', info=info, cherror=cherror, posinfo=posinfo, error=error, chinfo=chinfo)

@app.route('/update', methods=['POST'])
def update():
    error = None
    chinfo = None
    name = request.form['fname']
    surname = request.form['lname']
    email = request.form['email']
    color = request.form['color']
    about = request.form['about']
    
    if name.isalnum() == False:
        error = "Illegal First Name"
    elif surname.isalnum() == False:
        error = "Illegal Last Name"
    elif email == "":
        error = "Empty email field"
    elif not re.match(r"^[a-zA-Z0-9._-]+\@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$", email):
        error = "Invalid email address"
    elif re.search(r"[<>=/\+\?\.\*\^\$\(\)\[\]\{\}\|\\]{1,}", about):
        error = "Filed 'about' contains invalid characters"
    else:
        chinfo = "Profile updated"
        g.db.execute("UPDATE users SET name=?, surname=?, email=?, color=?, about=? WHERE username=?", [name, surname, email, color, about, session['logged_user']])
        g.db.commit()
    return profile(error=error, chinfo=chinfo)

@app.route('/changepass', methods=['POST'])
def changepass():
    cherror = None
    posinfo = None
    cur = g.db.execute('SELECT password FROM users WHERE username=?', [session['logged_user']])
    password = cur.fetchall()
    password = password[0][0]
    old_pass = request.form['old_pass']
    new_pass = request.form['new_pass']
    re_new_pass = request.form['re_new_pass']
    
    if old_pass == "" or new_pass == "" or re_new_pass == "":
        cherror = "Empty field"
    elif len(new_pass) < 5:
        cherror = "Password too short"
    elif not compare_password(old_pass, password):
        cherror = "Wrong old password"
    elif new_pass != re_new_pass:
        cherror = "New password doesn't match"
    else:
        g.db.execute("UPDATE users SET password=? WHERE username=?", [hash_password(new_pass), session['logged_user']])
        g.db.commit()
        posinfo = "Password succesfully changed"
    return profile(cherror=cherror, posinfo=posinfo)

@app.route('/database', methods=['GET'])
def database():
    cur = g.db.execute('SELECT id, username, password, name, surname, email, color, about, ip FROM users ORDER BY id DESC')
    users = [dict(id=row[0], username=row[1], password=row[2], name=row[3], surname=row[4], email=row[5], color=row[6], about=row[7], ip=row[8]) for row in cur.fetchall()]
    return render_template('database.html', users=users)

@app.route('/delete', methods=['POST'])
def delete():
    g.db.execute('DELETE FROM users WHERE username = ?', [request.form['username']])
    g.db.execute('DELETE FROM entries WHERE author = ?', [request.form['username']])
    g.db.commit()
    return redirect(url_for('database'))

@app.route('/view')
def view():
    author = request.args.get('author')
    cur = g.db.execute('SELECT name, surname, email, color, about FROM users WHERE username=?', [author])
    info = [dict(name=row[0], surname=row[1], email=row[2], color=row[3], about=row[4]) for row in cur.fetchall()]
    dur = g.db.execute('SELECT text, data FROM entries WHERE author=? ORDER BY id DESC', [author])
    forts = [dict(entry=row[0], data=row[1]) for row in dur.fetchall()]
    return render_template('view.html', info=info, forts=forts, author=author)

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = random_string()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8000, debug=True, ssl_context=('certifacates/server.crt', 'certifacates/server.key'))
