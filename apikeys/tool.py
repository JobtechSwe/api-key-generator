import smtplib
import ssl
import os
import sys
import logging
from apikeys import settings
from apikeys.repository import postgres, update_elastic


log = logging.getLogger(__name__)


def send_link_email(recipient, key):
    host = os.getenv('HOST_URL')
    if not host:
        log.error("No HOST_URL environment variable specified. Exit!")
        sys.exit(1)
    try:
        if not host.startswith('http'):
            host = 'https://' + os.getenv('HOST_URL')
        log.debug("HOST_URL environment set to: %s" % host)
        context = ssl.create_default_context()
        server = smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        message = "To: {recipient}\nSubject: Your link to API key for JobtechDev\n\n" + \
                  "Thank You for building applications using JobTech's APIs.\n\n" + \
                  "We hope You will find them easy to use and that Your application will help" + \
                  " employees and employers to find each other.\n" + \
                  "By following the link You will get Your API key {host}/key/{key}\n" + \
                  "If You have any questions, please send an e-mail to jobtechdev@arbetsformedlingen.se\n" \
                  "Thank You!\n\n" + \
                  "Best regards, The JobTech API teams"

        server.sendmail(settings.MAIL_SENDER, recipient,
                        message.format(recipient=recipient, host=host, key=key))

        log.info(f"Sending email to {recipient} containing link {host}/key/{key}")
    except smtplib.SMTPRecipientsRefused as e:
        log.error("Failed to send email to %s: %s" % (recipient, str(e)))
    except smtplib.SMTPException as e:
        log.warning("Failed to send email %s: %s. Trying again later."
                    % (recipient, str(e)))
        return False
    except Exception as e:
        log.error("Failed to send email %s: %s. Trying again later."
                  % (recipient, str(e)))
        return False
    return True


# Console script to update keys in elastic
def update():
    update_elastic()


def start():
    recipients = postgres.get_unsent_keys()
    for recipient in recipients:
        if send_link_email(recipient[0], recipient[1]):
            postgres.set_sent_flag(recipient[0], 1)


if __name__ == '__main__':
    start()
