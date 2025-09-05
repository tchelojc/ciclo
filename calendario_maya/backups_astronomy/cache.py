import time
from functools import wraps

def cache(ttl=3600):
    """Decorador para cache com tempo de vida"""
    def decorator(func):
        cache_data = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = time.time()
            
            if key in cache_data:
                data, timestamp = cache_data[key]
                if now - timestamp < ttl:
                    return data
            
            data = func(*args, **kwargs)
            cache_data[key] = (data, now)
            return data
            
        return wrapper
    return decorator