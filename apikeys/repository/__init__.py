import logging
from . import postgres
from . import elastic

log = logging.getLogger(__name__)


def update_elastic():
    apps = postgres.get_available_applications()
    for app in apps:
        keys = postgres.get_keys_for_api(app['id'])
        if keys:
            log.info("Updating keys in Elastic for %s" % app['name'])
            elastic.store_keys(app['name'], keys)
        else:
            log.info("No keys found for %s - skipping update in Elastic" % app['name'])
