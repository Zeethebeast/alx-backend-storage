#!/usr/bin/env python3
"""
Module for a Cache class to interact with a Redis database.
"""

import redis
import uuid
import requests
from typing import Union, Callable, Optional
from functools import wraps

cache = redis.Redis()

def count_calls(method: Callable) -> Callable:
    """A decorator that counts the number of times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs in Redis."""
    @wraps(method)
    def wrapper(self, *args):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        self._redis.rpush(input_key, str(args))
        result = method(self, *args)
        self._redis.rpush(output_key, result)
        
        return result
    return wrapper

def replay(method: Callable) -> None:
    """Display the call history of a function, including inputs and outputs."""
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"
    self = method.__self__

    inputs = self._redis.lrange(input_key, 0, -1)
    outputs = self._redis.lrange(output_key, 0, -1)
    
    call_count = len(inputs)
    print(f"{method.__qualname__} was called {call_count} times:")
    
    for inp, out in zip(inputs, outputs):
        inp_decoded = inp.decode("utf-8")
        out_decoded = out.decode("utf-8")
        print(f"{method.__qualname__}(*{inp_decoded}) -> {out_decoded}")

def count_requests(method: Callable) -> Callable:
    """Decorator to count requests to a particular URL."""
    @wraps(method)
    def wrapper(url: str) -> str:
        cache.incr(f"count:{url}")
        return method(url)
    return wrapper

@count_requests
def get_page(url: str) -> str:
    """Fetch HTML content from a URL with caching for 10 seconds."""
    cached_content = cache.get(f"cache:{url}")
    if cached_content:
        return cached_content.decode("utf-8")
    
    response = requests.get(url)
    content = response.text
    
    cache.setex(f"cache:{url}", 10, content)  # Cache with 10-second expiration
    return content

class Cache:
    """A Cache class that provides methods to store data in a Redis database."""

    def __init__(self, host='localhost', port=6379):
        self._redis = redis.Redis(host=host, port=port)
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores data in Redis with a randomly generated UUID as the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
    
    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieves a string value from Redis by decoding the bytes as UTF-8."""
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """Retrieves an integer value from Redis by converting the bytes to an integer."""
        return self.get(key, fn=int)
