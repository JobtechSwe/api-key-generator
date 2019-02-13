from apikeys import app
from apikeys import repository
from flask import render_template, request, flash


@app.route('/')
def hello():
    return render_template('base.html')


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    app_id = request.form['appid']
    error = None

    if not email:
        error = 'Email is required'

    if error is not None:
        flash(error)

    print("E-postadress: %s" % email)
    key = repository.create_api_key(email)
    ticket = repository.store_key(key, email, None, app_id)

    print("KEY: %s" % key)
    print("ADDRESS: http://localhost:5000/key/%s" % ticket)

    return render_template('registered.html')


@app.route("/key/<ticket>", methods=['GET'])
def showkey(ticket):
    key = repository.get_key_for_ticket(ticket)
    return f"Your API key is <b>{key}</b>"

