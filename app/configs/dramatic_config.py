import dramatiq
from dramatiq.brokers.redis import RedisBroker

redis_broker = RedisBroker(host="redis", port=6379, db=1)
dramatiq.set_broker(redis_broker)
