import os
import redis
from rq import Worker, Queue, Connection

__all__ = ['redis_conn']

_listen = ['default']
_redis_url = os.getenv('REDISTOGO_URL', 'redis://:my_redis_pass@localhost:6379')
redis_conn = redis.from_url(_redis_url)


if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(list(map(Queue, _listen)))
        worker.work()
