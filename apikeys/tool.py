import smtplib, ssl
from apikeys import settings
from apikeys.repository import postgres


def send_link_email(recipient, key):
    context = ssl.create_default_context()
    server = smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
    message = f"Subject: Din API-nyckel hos JobtechDev\n\n" + \
              "Ladda ner din API-nyckel: http://localhost:5000/key/{key}"

    server.sendmail(settings.MAIL_SENDER, recipient, message)

    print(f"Sending email to {recipient} containing link http://localhost:5000/key/{key}")
    return False


def start():
    recipients = postgres.get_unsent_keys()
    for recipient in recipients:
        if send_link_email(recipient[0], recipient[1]):
            postgres.set_sent(recipient[0], 1)


if __name__ == '__main__':
    start()