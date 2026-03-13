import pika


class RabbitMQProducer:
    def __init__(self, connector, queue_name):
        self.connection = connector.create_connection()
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def publish(self, message):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[x] Sent: {message}")

    def close(self):
        self.connection.close()




