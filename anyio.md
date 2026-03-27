# AnyIO

## creating and managing tasks

```python
async with create_task_group() as tg:
    tg.start_soon(task_coro)
```

or

```python
tg = create_task_group()

tg.__aenter__()

tg.start_soon(task_coro)

tg.__aexit__()
```

or

```python
async def start_some_service(task_status = TASK_STATUS_IGNORED):
    task_status.started()

    await some_service(...)

async with create_task_group() as tg:
    tg.start(start_some_service)

    tg.start_soon(...)
```

## cancellation and timeouts

cancellation:

```python
async def waiter():
    try:
        await sleep(1)
    except get_cancelled_exc_class():
        raise

async def task():
    async with create_task_group() as tg:
        tg.start_soon(waiter)
        await sleep(0.5)
        tg.cancel_scope.cancel()
```

timeout:

```python

async def task():
    async with create_task_group() as tg:
        with move_on_after(1) as scope:
            await sleep(2)
            print('This should never be printed')

```


### using synchronization primitives

events:

```python
event = Event()
await event.wait()
event.set()
```
semaphores:

```python
semaphore = Semophore(2)

async with semaphore:
    ...
```

locks:

```python
lock = Lock()

async with lock:
    ...
```

conditions:

```python
condition = Condition()

async with condition:
    await condition.wait()
    ...

async with condition:
    condition.notify(1)

async with condition:
    condition.notify(2)

async with condition:
    condition.notify_all()
```

capacity limiters:

```python
limiter = CapacityLimiter(2)

async with limiter:
    ...
```

resource guards:

```python
guard = ResourceGuard()

with guard:
    ...
```

## streams

```python
send_stream, receive_stream = create_memory_object_stream[str]()

async with send_stream:
    await send_stream.send("...")

async with receive_stream:
    async for item in receive_stream:
        print(item)
```

buffered byte streams:

```python
send, receive = create_memory_object_stream[bytes](4)
buffered = BufferedByteReceiveStream(receive)
for part in b'hel', b'lo, ', b'wo', b'rld!':
    await send.send(part)

result = await buffered.receive_exactly(8)
...
```

## threads

running a function in a worker thread:

```python
await to_thread.run_sync(time.sleep, 2)
```

calling async code from a worker thread:

```python
from_thread.run(anyio.sleep, 1)
```

calling sync code from a worker thread:

```python
from_thread.run_sync(time.sleep, 1)
```

accessing the event loop from a foreign thread:

option 1: event loop token

```python
from anyio.lowlevel import current_token
from anyio import from_thread

token = current_token()
thread = Thread(target=external_func, args=[token])
event = Event()

def external_func(token):
    from_thread.run_sync(event.set, token)
```

option 2: blocking portals

```python
def sync_func_in_thread(portal: BlockingPortal):
    portal.call(async_func)

async with BlockingPortal() as portal:
    await to_thread.run_sync(sync_func_in_thread, portal)
```

spawning tasks from the blocking portal:

```python
async def long_running_task():
    ...

portal.stark_task_soon(long_running_task)
```

reacting to cancellation in worker threads:

```python
def sync_func():
    while True:
        from_thread.check_cancelled()
        time.sleep(1)

with move_on_after(2):
    await to_thread.run_sync(sync_func)
```
