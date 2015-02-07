import sqlite3
import uuid
from flask import Flask, g, render_template, redirect, request, session, url_for

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods = ['GET', 'POST'])
def index():
	'''
	If the session is new, generate a new session id.
	Read and write session data.
	'''

	if 'id' not in session:
		app.logger.debug("Generating new session id")
		session['id'] = uuid.uuid4().hex

	if request.method == 'POST':
		get_db().execute('insert or replace into sessions values (?, ?)', (session['id'], request.form['data']))
		get_db().commit()
	data = get_db().execute('select session_data from sessions where session_id=?', (session['id'],)).fetchone()
	if data is not None:
		session['data'] = data[0]
	else:
		session['data'] = None

	return render_template('mobisession.html', **locals())

@app.route('/<session_id>')
def get_session(session_id=None):
	'''
	Sets the session id and redirects to index.
	'''
	if session_id is not None:
		app.logger.debug("Using stored session id")
		session['id'] = session_id

	return redirect(url_for('index'))

app.secret_key = 'Change me'

if __name__ == '__main__':
	app.run(debug=True)

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()
