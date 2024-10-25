#!/usr/bin/env python3
"""
Module for a Cache class to interact with a Redis database.
"""

import redis
import uuid
from typing import Union


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
