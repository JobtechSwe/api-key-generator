from apikeys.repository import postgres


def start():
    recipients = postgres.get_unsent_keys()
    for recipient in recipients:
        print(recipient)
        postgres.set_sent(recipient[1])


if __name__ == '__main__':
    start()
