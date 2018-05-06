from target import TargetCache
from lru import lru_cache as lru

cache = TargetCache()

__all__ = ['lru', 'cache']
