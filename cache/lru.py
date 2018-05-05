import logging
import time

logger = logging.getLogger(__name__)

def lru_cache(max_size=1000):
    cache = {}
    last_used = {}

    def lru_decorator(function):
        def wrapper(*args, **kwargs):
            s = '%s_%s' % (args, kwargs)
            last_used[s] = time.time()
            logger.debug('Updating LRU %s last used: %.10f', s, last_used[s])
            if s in cache:
                logger.debug('LRU cache hit: %s', s)
                return cache[s]

            result = function(*args, **kwargs)
            if len(cache) >= max_size:
                oldest_item = last_used[s]
                for item in cache.keys():
                    if last_used[item] < oldest_item:
                        oldest_item = last_used[item]

                logger.debug('LRU evicting %s (%.10f)', item, oldest_item)
                del cache[item]

            cache[s] = result

            return result
        return wrapper
    return lru_decorator
