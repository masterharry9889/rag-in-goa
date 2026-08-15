# Placeholder for retry policy
import time
import random
from typing import Callable, Any

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
):
    """
    Retry a function with exponential backoff and optional jitter.
    """
    def wrapper(*args, **kwargs):
        delay = base_delay
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == max_retries - 1:
                    raise e
                delay *= exponential_base
                if jitter:
                    delay *= random.uniform(0.5, 1.5)
                delay = min(delay, max_delay)
                time.sleep(delay)
        return func(*args, **kwargs)
    return wrapper