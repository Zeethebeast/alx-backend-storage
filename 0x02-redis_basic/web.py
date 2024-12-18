#!/usr/bin/env python3
"""
Module to fetch and cache HTML content of a URL with Redis, counting requests.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis client
cache = redis.Redis()


def count_requests(method: Callable) -> Callable:
    """Decorator to count requests to a particular URL."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper that increments the access count for the URL."""
        cache.incr(f"count:{url}")
        return method(url)
    return wrapper


@count_requests
def get_page(url: str) -> str:
    """
    Fetch HTML content from a URL with caching for 10 seconds.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        str: The HTML content of the URL.
    """
    cached_content = cache.get(f"cache:{url}")
    if cached_content:
        return cached_content.decode("utf-8")

    response = requests.get(url)
    content = response.text
    cache.setex(f"cache:{url}", 10, content)

    return content
