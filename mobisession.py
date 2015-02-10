import cStringIO, qrcode, sqlite3, uuid
from flask import Flask, g, render_template, redirect, request, send_file, session, url_for

app = Flask(__name__)

DATABASE = 'database.db'
SERVER_IP = '192.168.0.12:5000'
STATIC_DIR = 'static'

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

	if 'sid' not in session:
		app.logger.debug("Generating new session id")
		session['sid'] = uuid.uuid4().hex

	if request.method == 'POST':
		get_db().execute('insert or replace into sessions values (?, ?)', (session['sid'], request.form['data']))
		get_db().commit()
	data = get_db().execute('select session_data from sessions where session_id=?', (session['sid'],)).fetchone()
	if data is not None:
		session['data'] = data[0]
	else:
		session['data'] = None

	return render_template('mobisession.html', **locals())

@app.route('/session/<session_id>')
def get_session(session_id):
	'''
	Sets the session id and redirects to index.
	'''
	app.logger.debug("Using stored session id")
	session['sid'] = session_id

	return redirect(url_for('index'))

@app.route('/qr.png')
def get_qr():
	message = "".join(("http://", SERVER_IP, '/session/', session['sid']))
	app.logger.debug("Message: " + message)
	img = qrcode.make(message)
	img_buf = cStringIO.StringIO()
	img.save(img_buf)
	img_buf.seek(0)
	return send_file(img_buf, mimetype='image/png')

@app.route('/static/<path:filename>')
def get_static(filename):
	return send_from_directory(STATIC_DIR, filename)

app.secret_key = 'Change me'

if __name__ == '__main__':
	# Deleting the host parameter will only make the app reachable from
	# the local host.
	app.run(host='0.0.0.0', debug=True)

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()
