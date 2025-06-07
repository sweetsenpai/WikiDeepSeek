import asyncio

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.services.wiki_httpx import run_parser

redis_broker = RedisBroker(host="redis", port=6379, db=1)
dramatiq.set_broker(redis_broker)


@dramatiq.actor
def parser_wrapper(url):
    try:
        asyncio.run(run_parser(url))
    except Exception as e:
        print(f"Error in parser_wrapper: {e}")
        raise
