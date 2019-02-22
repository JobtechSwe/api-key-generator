from apikeys import app
from apikeys.repository import update_elastic, postgres
from flask import render_template, request


@app.route('/', methods=['GET'])
def hello():
    available_apis = postgres.get_available_applications()
    return render_template('form.html', app_list=available_apis)


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    appids = request.form.getlist('appid')
    if not email:
        return "Du måste ange en e-postadress."

    app_id = 0
    for aid in appids:
        app_id = app_id | int(aid)

    userinfo = {
        "name": request.form.get('name'),
        "surname": request.form.get('surname'),
        "company_name": request.form.get('companyname'),
        "application_name": request.form.get('applicationname'),
        "description": request.form.get('description'),
    }

    key = postgres.create_api_key(email)
    ticket = postgres.store_key(key, email, userinfo, app_id)
    update_elastic()

    print("ADDRESS: http://localhost:5000/key/%s" % ticket)

    return render_template('registered.html', email=email)


@app.route("/key/<ticket>", methods=['GET'])
def showkey(ticket):
    key = postgres.get_key_for_ticket(ticket)
    if not key:
        return render_template("failed_key.html", ticket=ticket)
    postgres.set_visited(ticket)
    return render_template('key.html', key=key)


@app.route("/retrieve_key", methods=['POST'])
def retrieve_key():
    email = request.form.get('email')
    ticket = request.form.get('ticket')

    if not email:
        return "Du måste ange en e-postadress."
    if not ticket:
        return "Formuläret saknas nödvändig data."

    postgres.set_sent_flag(email, 0)
    postgres.set_visited(ticket, force=True)

    return render_template('registered.html', email=email)


@app.route("/showbits/<number>", methods=['GET'])
def showbits(number):
    list = [int(x) for x in "{:08b}".format(int(number))]
    print(list)
    n = 0
    ids = []
    for l in list:
        num = (l*2)**(7-n)
        print(num)
        ids.append(num)
        n += 1
    return str(ids)