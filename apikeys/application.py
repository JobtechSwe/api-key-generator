import logging
from jobtech.common.customlogging import configure_logging
from apikeys import app
from apikeys.repository import update_elastic, postgres
from flask import render_template, request, flash, abort, redirect


configure_logging([__name__.split(".")[0]])
log = logging.getLogger(__name__)
log.info(logging.getLevelName(log.getEffectiveLevel()) + ' log level activated')
log.info("Starting %s" % __name__)


@app.route('/', methods=['GET'])
def hello():
    available_apis = postgres.get_available_applications()
    return render_template('form.html', app_list=available_apis)


@app.route('/register', methods=['POST'])
def register():
    log.debug("Serving request for /register: %s" % request.values)
    email = request.form['email']
    appids = request.form.getlist('appid')
    application_name = request.form.get('applicationname')
    if not request.form.get('approve_gdpr', None):
        log.debug("User has not approved GDPR, sending back to base page")
        flash("You must approve our handling of your details.")
        return redirect("/")
    if not request.form.get('approve_licence', None):
        log.debug("User has not approved licence, sending back to base page")
        flash("You must approve our usage licence.")
        return redirect("/")
    if not email:
        log.debug("User has provided an email address, sending back to base page")
        flash("You must provide an email address")
        return redirect("/")

    app_id = 0
    for aid in appids:
        app_id = app_id | int(aid)
    if app_id == 0:
        log.debug("User has not selected an API, sending back to base page")
        flash("You need to select at least one API")
        return redirect("/")
    if not application_name:
        log.debug("User has not entered an application name, sending back to base page")
        flash("You need to enter an application name")
        return redirect("/")

    userinfo = {
        "name": request.form.get('name'),
        "surname": request.form.get('surname'),
        "company_name": request.form.get('companyname'),
        "application_name": request.form.get('applicationname'),
        "description": request.form.get('description'),
    }

    key = postgres.create_api_key(email)
    ticket = postgres.store_key(key, email, application_name, userinfo, app_id)
    log.debug("Generated ticket %s for %s" % (ticket, email))
    update_elastic()

    return render_template('registered.html', email=email)


@app.route("/key/<ticket>", methods=['GET'])
def showkey(ticket):
    key = postgres.get_key_for_ticket(ticket)
    if not key:
        return render_template("failed_key.html", ticket=ticket)
    log.debug("Showing API key for ticket %s" % ticket)
    postgres.set_visited(ticket)
    return render_template('key.html', key=key)


@app.route("/retrieve_key", methods=['POST'])
def retrieve_key():
    email = request.form.get('email')
    ticket = request.form.get('ticket')

    if not ticket:
        abort(400)
    if not email:
        flash("You must provide an email address")
        return redirect("/key/%s" % ticket)
    else:
        log.debug("Preparing to resend email to %s" % email)
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
