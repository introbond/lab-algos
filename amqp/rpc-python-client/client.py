from mockup_tasks import generate_mockup_tasks

import pika
import uuid
import time

class RPCClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.11.61'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.correlation_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.correlation_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id,
            ),
            body=str(n))

        start_time = time.time()  # record the time before processing

        while self.response is None:
            self.connection.process_data_events()

        processing_time = time.time() - start_time  # calculate processing time after response is received

        print(f"Processing time: {processing_time} seconds")  # print processing time

        return self.response

rpc_client = RPCClient()

tasks = generate_mockup_tasks()
response = rpc_client.call(tasks)
print("Response:", response.decode())
