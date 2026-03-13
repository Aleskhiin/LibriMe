import pika


class RabbitMQConnector:
    def __init__(self, host='localhost'):
        self.host = host

    def create_connection(self):
        return pika.BlockingConnection(pika.ConnectionParameters(self.host))



