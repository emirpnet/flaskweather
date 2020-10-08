# flaskweather/run_local.py
# Version: --
# Author : Jochen Peters

from flask import Flask, redirect
from flaskweather import fw_bp

app = Flask(__name__)
app.register_blueprint(fw_bp)

# routes
@app.route('/')
def baseurl():
	return redirect('/weather')

# run
if __name__ == '__main__':
	# remote_access setting is ignored
	app.run(host='127.0.0.1', port=8080, debug=True)
