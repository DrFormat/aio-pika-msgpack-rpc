import time
from typing import Any

import msgpack
from aio_pika.message import DeliveryMode, IncomingMessage, Message
from aio_pika.patterns.rpc import RPC, RPCMessageTypes


class MSGPackRPC(RPC):
    SERIALIZER = msgpack
    CONTENT_TYPE = 'application/x-msgpack'

    def serialize(self, data: Any) -> bytes:
        return self.SERIALIZER.packb(data, use_bin_type=True, default=repr)

    def deserialize(self, data: Any) -> bytes:
        result = self.SERIALIZER.unpackb(data, use_list=False, raw=False)
        if isinstance(result, dict):
            exception = result.get('exception')
            if exception:
                result = eval(exception)  # pylint: disable=eval-used
        return result

    def serialize_exception(self, exception: Exception) -> bytes:
        return self.serialize({'exception': repr(exception)})

    async def call(
        self,
        method_name,
        kwargs: dict = None,
        *,
        expiration: int = None,
        priority: int = 5,
        delivery_mode: DeliveryMode = RPC.DELIVERY_MODE
    ):
        future, correlation_id = self.create_future()

        headers = {'From': self.result_queue.name}

        message = Message(
            body=self.serialize(kwargs or {}),
            type=RPCMessageTypes.CALL.value,
            timestamp=time.time(),
            priority=priority,
            correlation_id=correlation_id,
            delivery_mode=delivery_mode,
            reply_to=self.result_queue.name,
            headers=headers
        )

        if expiration is not None:
            message.expiration = expiration

        await self.channel.default_exchange.publish(message, routing_key=method_name, mandatory=True)
        return await future

    async def on_call_message(self, method_name: str, message: IncomingMessage):
        await super().on_call_message(method_name, message)
