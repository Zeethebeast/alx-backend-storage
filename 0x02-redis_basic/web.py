#!/usr/bin/env python3

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
        # Increment the access count for the URL
        cache.incr(f"count:{url}")
        return method(url)
    return wrapper

@count_requests
def get_page(url: str) -> str:
    """Fetch HTML content from a URL with caching for 10 seconds."""
    # Check if content is cached
    cached_content = cache.get(f"cache:{url}")
    if cached_content:
        return cached_content.decode("utf-8")
    
    # Fetch content from the URL if not cached
    response = requests.get(url)
    content = response.text
    
    # Cache the content with a 10-second expiration
    cache.setex(f"cache:{url}", 10, content)
    
    return content
