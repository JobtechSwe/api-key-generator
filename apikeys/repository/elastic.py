import certifi
from ssl import create_default_context
from elasticsearch import Elasticsearch
from apikeys import settings

if settings.ES_USER and settings.ES_PWD:
    context = create_default_context(cafile=certifi.where())
    es = Elasticsearch([settings.ES_HOST], port=settings.ES_PORT,
                       use_ssl=True, scheme='https', ssl_context=context,
                       http_auth=(settings.ES_USER, settings.ES_PWD))
else:
    es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])


def store_keys(api, keys):
    doc_id = api
    es.index(index='apikeys', id=doc_id, body=keys)
