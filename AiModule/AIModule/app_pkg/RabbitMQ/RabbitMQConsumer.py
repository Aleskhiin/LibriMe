import threading


class RabbitMQConsumer(threading.Thread):
    def __init__(self, connector, queue_name, callback):
        super().__init__()
        self.connector = connector
        self.queue_name = queue_name
        self.callback = callback

    def run(self):
        connection = self.connector.create_connection()
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        print(f"[*] Consumer for '{self.queue_name}' started.")
        channel.start_consuming()


