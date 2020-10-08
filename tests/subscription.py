import time
import redis

REDIS_CONFIG = {"host": "localhost", "port": 6379, "db": 0}
REDIS_CHANNEL = "upscoot"

r = redis.Redis(**REDIS_CONFIG, decode_responses=True)
pubsub = r.pubsub(ignore_subscribe_messages=True)
someval = 10

pubsub.subscribe(REDIS_CHANNEL)

while True:
    msg = pubsub.get_message()
    if msg:
        print(msg)
    time.sleep(.1)
