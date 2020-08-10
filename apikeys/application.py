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

    if not _validate_form(request, appids):
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

    userinfo = {k: request.form.get(k) for k, v in dict(request.form).items()
                if k in ['name', 'surname', 'corporation', 'companyname',
                         'company_phone_number', 'company_address', 'phone_number',
                         'address', 'applicationname', 'description']}

    key = postgres.create_api_key(email)
    ticket = postgres.store_key(key, email, application_name, userinfo, app_id)
    log.debug("Generated ticket %s for %s" % (ticket, email))
    update_elastic()

    return render_template('registered.html', email=email)


APP_ID_JOB_SEARCH = '3'
APP_ID_JOB_STREAM_BULK = '16'
# APP_ID_TAXONOMY = '8'
# APP_ID_JOBAD_ENRICHMENTS = '64'

def _validate_form(req, appids):
    if not req.form.get('approve_gdpr'):
        log.debug("User has not approved GDPR, sending back to base page")
        flash("You must approve our handling of your details.")
        return False
    if (APP_ID_JOB_SEARCH in appids or APP_ID_JOB_STREAM_BULK in appids) and not req.form.get('approve_licence'):
        log.debug("User has not approved license for Job Search API and Job Stream Bulk API, sending back to base page")
        flash("You must approve our usage license for Job Search API and Job Stream Bulk API.")
        return False
    if not req.form.get('email'):
        log.debug("User has provided an email address, sending back to base page")
        flash("You must provide an email address")
        return False
    if req.form.get('corporation', '0') == '1':
        # Check form for company information
        if not req.form.get('companyname'):
            log.debug("No company name provided")
            flash("You must provide company name")
            return False
        if not req.form.get('company_address'):
            log.debug("User has not provided an address")
            flash("You must provide an address")
            return False
        if not req.form.get('company_phone_number'):
            log.debug("User has not provided a phone number")
            flash("You must provide a phone number")
            return False

    else:
        if not req.form.get('address'):
            log.debug("User has not provided an address")
            flash("You must provide your home address")
            return False
        if not req.form.get('phone_number'):
            log.debug("User has not provided a phone number")
            flash("You must provide your phone number")
            return False

    return True


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
        log.debug("Preparing to resend email to: %s" % email)
        postgres.set_sent_flag(email, 0)
        postgres.set_visited(ticket, force=True)

        return render_template('registered.html', email=email)
