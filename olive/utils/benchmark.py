"""
Utilities for benchmarkings. For now, only timer.

# TODO memory, cpu usage, network usage, disk io
"""
import asyncio
import time

__all__ = ["timeit"]


def timeit(func):
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            print("this function is a coroutine: {}".format(func.__name__))
            return await func(*args, **params)
        else:
            print("this is not a coroutine")
            return func(*args, **params)

    async def helper(*args, **params):
        print("{}.time".format(func.__name__))
        start = time.time()
        result = await process(func, *args, **params)

        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)

        print(">>>", time.time() - start)
        return result

    return helper
