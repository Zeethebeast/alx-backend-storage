#!/usr/bin/env python3
"""
Module for a Cache class to interact with a Redis database.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from typing import Union, Callable, Optional
from functools import wraps

class Cache:
    """
    A Cache class that provides methods to store data in a Redis database.

    Attributes:
        _redis (redis.Redis): A Redis client instance.
    """

    def __init__(self, host='localhost', port=6379):
        """
        Initializes the Cache instance with a Redis client and clears the database.

        Args:
            host (str): The hostname of the Redis server.
            port (int): The port number of the Redis server.
        """
        self._redis = redis.Redis(host=host, port=port)
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores data in Redis with a randomly generated UUID as the key.

        Args:
            data (Union[str, bytes, int, float]): The data to store in Redis.

        Returns:
            str: The key associated with the stored data in Redis.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
    

    
    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieves data from Redis and optionally applies a conversion function.

        Args:
            key (str): The Redis key.
            fn (Optional[Callable]): A function to convert the data to the desired format.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data, converted if fn is provided,
                                                 or None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieves a string value from Redis by decoding the bytes as UTF-8.

        Args:
            key (str): The Redis key.

        Returns:
            Optional[str]: The retrieved data as a string, or None if the key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieves an integer value from Redis by converting the bytes to an integer.

        Args:
            key (str): The Redis key.

        Returns:
            Optional[int]: The retrieved data as an integer, or None if the key does not exist.
        """
        return self.get(key, fn=int)
    
def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts the number of times a method is called.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The decorated method with call counting functionality.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Generate the key based on the method's qualified name
        key = method.__qualname__
        # Increment the call count in Redis
        self._redis.incr(key)
        # Call the original method and return its result
        return method(self, *args, **kwargs)
    
    return wrapper