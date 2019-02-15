from apikeys.repository import postgres


def send_link_email(recipient, key):
    print(f"Sending email to {recipient} containing link http://localhost:5000/key/{key}")
    return False


def start():
    recipients = postgres.get_unsent_keys()
    for recipient in recipients:
        if send_link_email(recipient[0], recipient[1]):
            postgres.set_sent(recipient[0])


if __name__ == '__main__':
    start()
