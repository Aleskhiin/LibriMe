import pika

def connect_to_rabbitmq():
    """
    Establishes a connection to the RabbitMQ server and returns the channel.
    
    Returns:
        pika.channel.Channel: The channel to communicate with RabbitMQ.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    return channel

def setup_queue(channel, queue_name='test_queue'):
    """
    Declares a queue on the RabbitMQ server.

    Args:
        channel (pika.channel.Channel): The RabbitMQ channel.
        queue_name (str): Name of the queue to declare.
    """
    channel.queue_declare(queue=queue_name)

def send_message(channel, queue_name='test_queue', message='Hello RabbitMQ!'):
    """
    Sends a message to the specified RabbitMQ queue.

    Args:
        channel (pika.channel.Channel): The RabbitMQ channel.
        queue_name (str): Name of the queue.
        message (str): Message to send.
    """
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(f"Sent: {message}")

def receive_message(channel, queue_name='test_queue'):
    """
    Receives a single message from the specified RabbitMQ queue.

    Args:
        channel (pika.channel.Channel): The RabbitMQ channel.
        queue_name (str): Name of the queue.
    """
    def callback(ch, method, properties, body):
        print(f"Received: {body.decode()}")
        ch.stop_consuming()

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("Waiting for message...")
    channel.start_consuming()

if __name__ == "__main__":
    channel = connect_to_rabbitmq()
    setup_queue(channel)
    send_message(channel)
    receive_message(channel)
