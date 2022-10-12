# aio-pika-msgpack-rpc
 
Requires Python >= 3.7.

## Installation
```
pip install aio-pika-msgpack-rpc
```

## Example
```python
import asyncio
import aio_pika
from aio_pika_msgpack_rpc import MSGPackRPC


async def main():
    client = await aio_pika.connect_robust('amqp://guest:guest@localhost:5672/')
    channel = await client.channel()
    rpc = await MSGPackRPC.create(channel)

    # rpc calls
    result = await rpc.call('method_name', kwargs={'test': 'data'})

asyncio.get_event_loop().run_until_complete(main())

```