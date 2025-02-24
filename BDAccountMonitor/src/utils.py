def exp_retry(retrycount, initial_backoff=10):
    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            iteration = 0
            backoff = initial_backoff
            while iteration < retrycount:
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    print(f'{f.__name__} failed for the iteration {iteration} with {e}')
                
                iteration += 1
                if iteration < retrycount:
                    backoff *= 2
                    print(f'Waiting for {backoff} seconds then retry...')
                    await asyncio.sleep(backoff)
                    print(f'Retrying for {f.__name__}, iteration: {iteration}')
                else:
                    print(f'Exceeded max retry count for {f.__name__}.')
                    raise Exception(f'Exceeded max retry count for {f.__name__}.')
        return wrapped
    return decorator

@exp_retry(3)
async def with_retry(func, *args, **kwargs):
    return await func(*args, **kwargs)