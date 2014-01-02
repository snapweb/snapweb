import gevent.monkey
gevent.monkey.patch_all()

import datetime
import json
import urlparse

import requests
from flask import Flask, render_template, request, redirect, url_for, make_response, g, Response
from flask_bootstrap import Bootstrap
from functools import wraps
from pysnap import Snapchat, is_image
from wtforms import Form, TextField, PasswordField, validators


app = Flask(__name__)
Bootstrap(app)


class LoginForm(Form):
    username = TextField('Snapchat username', [validators.Length(min=4)])
    password = PasswordField('Snapchat password', [validators.Required()])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        snapchat = Snapchat()
        snapchat.login(form.username.data, form.password.data)

        rsp = make_response(redirect(url_for('index')))
        rsp.set_cookie('username', snapchat.username)
        rsp.set_cookie('auth_token', snapchat.auth_token)
        return rsp

    return render_template('login.html', form=form)


def login_required(f):
    '''
    Decorator to verify that we have user's login token.  Sets up snapchat
    client provided by pysnap
    '''

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.cookies.get('auth_token')
        username = request.cookies.get('username')
        if not auth_token or not username:
            return redirect(url_for('login'))

        g.snapchat = Snapchat()
        g.snapchat.username = username
        g.snapchat.auth_token = auth_token

        rsp = f(*args, **kwargs)

        if not type(rsp) is Response:
            rsp = Response(rsp)

        # Snapchat API allows token to be updated during a request, keep cookie
        # in sync.
        rsp.set_cookie('auth_token', g.snapchat.auth_token)

        return rsp
    return decorated_function


@app.route('/logout')
def logout():
    rsp = make_response(redirect(url_for('login')))
    rsp.set_cookie('username', '', expires=0)
    rsp.set_cookie('auth_token', '', expires=0)
    return rsp


@app.route('/api/')
@app.route('/api/<function_name>')
@login_required
def api(function_name=None):
    '''Simple api to some functions exposed by pysnap'''

    supported = [
        'get_updates',
        'get_snaps',
        'get_friends',
        'get_best_friends',
        'get_blocked',
    ]

    if function_name is None:
        return json.dumps([
            urlparse.urljoin(request.url_root, 'api/%s' % rule) for rule in supported
        ])

    if not function_name in supported:
        return Response(status=404)

    func = getattr(g.snapchat, function_name)
    snap_rsp = func(**request.args)
    return json.dumps(snap_rsp)


@app.route('/snap/<snap_id>')
@login_required
def get_snap(snap_id):

    # Avoid re-downloading and decrypting content if possible.
    if 'If-Modified-Since' in request.headers:
        return Response(status=304)

    blob = g.snapchat.get_blob(snap_id)
    rsp = make_response(blob)
    if is_image(blob):
        rsp.headers['Content-Type'] = 'image/jpg'
    else:
        rsp.headers['Content-Type'] = 'video/mp4'

    rsp.headers['Last-Modified'] = datetime.datetime.now()

    return rsp


@app.route('/')
@login_required
def index():
    try:
        snaps = g.snapchat.get_snaps()
    except requests.HTTPError, e:
        if e.response.status_code == 401:
            return redirect(url_for('login'))

    return render_template(
        'index.html',
        username=g.snapchat.username,
        snaps=snaps
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
