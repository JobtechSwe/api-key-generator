import logging
from flask import Flask

app = Flask(__name__)


def configure_logging():
    logging.basicConfig()
    # Remove basicConfig-handlers and replace with custom formatter.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    stream_handler = logging.StreamHandler()

    root = logging.getLogger()
    # root.setLevel(logging.INFO)
    root.addHandler(stream_handler)

    set_custom_log_level()


def set_custom_log_level():
    # Set log level debug for module specific events
    # and level warning for all third party dependencies
    for key in logging.Logger.manager.loggerDict:
        # for handler in logging.getLogger(key).handlers[:]:
        #     logging.getLogger(key).removeHandler(handler)
        if key.startswith(__name__) or key.startswith('valuestore'):
            logging.getLogger(key).setLevel(logging.DEBUG)

        else:
            logging.getLogger(key).setLevel(logging.WARNING)


def setup_application():
    configure_logging()
    with app.app_context():
        # Enables routes in 'application.py'
        from apikeys import application

    log = logging.getLogger(__name__)
    log.debug(logging.getLevelName(log.getEffectiveLevel()) + ' log level activated')
    log.info("Starting %s" % __name__)


if __name__ == '__main__':
    # Used only when starting this script directly, i.e. for debugging
    setup_application()
    app.run(debug=True)
else:
    setup_application()
    print("Starting %s" % __name__)
