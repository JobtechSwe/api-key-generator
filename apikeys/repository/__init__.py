from . import postgres
from . import elastic


def update_elastic():
    apps = postgres.get_available_applications()
    for app in apps:
        keys = postgres.get_keys_for_api(app['id'])
        elastic.store_keys(app['name'], {"validkeys": keys})

