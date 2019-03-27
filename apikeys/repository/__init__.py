import logging
from . import postgres
from . import elastic

log = logging.getLogger(__name__)


def update_elastic():
    apps = postgres.get_available_applications()
    for app in apps:
        keys = postgres.get_keys_for_api(app['id'])
        log.info("Updating keys for %s" % app['name'])
        elastic.store_keys(app['name'], {"validkeys": keys})
