import json
import pika


class RabbitMQProducer:
    EXCHANGE = "job.exchange"
    ROUTING_KEY = "donejob.key"

    def __init__(self, connector):
        self.connection = connector.create_connection()
        self.channel = self.connection.channel()

    def publish(self, message: dict):
        self.channel.basic_publish(
            exchange=self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def close(self):
        self.connection.close()
