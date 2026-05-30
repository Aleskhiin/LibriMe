from .RabbitMQConsumer import RabbitMQConsumer


class RabbitMQManager:
    def __init__(self, connector):
        self.connector = connector
        self.consumers = []

    def add_consumer(self, queue_name, callback, count=1):
        for _ in range(count):
            consumer = RabbitMQConsumer(self.connector, queue_name, callback)
            self.consumers.append(consumer)

    def start_all(self):
        for consumer in self.consumers:
            consumer.start()

    def wait_for_all(self):
        for consumer in self.consumers:
            consumer.join()
