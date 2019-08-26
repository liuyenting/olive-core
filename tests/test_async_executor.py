import concurrent.futures
import asyncio
import time

def blocking(delay):
    time.sleep(delay)
    print('Completed.')

async def non_blocking(loop, executor):
    # Run three of the blocking tasks concurrently. asyncio.wait will
    # automatically wrap these in Tasks. If you want explicit access
    # to the tasks themselves, use asyncio.ensure_future, or add a
    # "done, pending = asyncio.wait..." assignment
    await asyncio.wait(
        fs={
            # Returns after delay=12 seconds
            loop.run_in_executor(executor, blocking, 12),

            # Returns after delay=14 seconds
            loop.run_in_executor(executor, blocking, 14),

            # Returns after delay=16 seconds
            loop.run_in_executor(executor, blocking, 16)
        },
        return_when=asyncio.ALL_COMPLETED
    )

loop = asyncio.get_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
loop.run_until_complete(non_blocking(loop, executor))