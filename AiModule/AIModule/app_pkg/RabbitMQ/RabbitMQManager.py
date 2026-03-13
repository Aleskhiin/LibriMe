import os
import yaml
from RabbitMQConsumer import RabbitMQConsumer
from RabbitMQConnector import RabbitMQConnector
from RabbitMQProducer import RabbitMQProducer



class RabbitMQManager:
    def __init__(self, connector):
        self.connector = connector
        self.consumers = []

    def add_consumer(self, queue_name, callback, count=1):  # FIX
        for _ in range(count):
            consumer = RabbitMQConsumer(self.connector, queue_name, callback)
            self.consumers.append(consumer)

    def start_all(self):
        for consumer in self.consumers:
            consumer.start()

    def wait_for_all(self):
        for consumer in self.consumers:
            consumer.join()



def load_config(path='config.yaml'):
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
def process_message(ch, method, properties, body):
    print(f"[x] Received: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(parent_dir, "Resources", "config.yaml")
    config = load_config(config_path)
    connector = RabbitMQConnector(config['rabbitmq']['host'])

    # Producer
    producer = RabbitMQProducer(connector, 'tasks')
    producer.publish("Hello from YAML config!")
    producer.close()

    # Manager
    manager = RabbitMQManager(connector)
    for queue in config['queues']:
        manager.add_consumer(queue['name'], process_message, queue['consumers'])

    manager.start_all()
    manager.wait_for_all()
