from unittest.mock import Mock
from app_pkg.RabbitMQ.RabbitMQConsumer import RabbitMQConsumer


def _make_connector():
    ch = Mock()
    ch.start_consuming.side_effect = KeyboardInterrupt
    conn = Mock()
    conn.channel.return_value = ch
    connector = Mock()
    connector.create_connection.return_value = conn
    return connector, ch


def test_consumer_declares_queue_as_non_durable():
    connector, ch = _make_connector()
    consumer = RabbitMQConsumer(connector, "newjob.queue", Mock())
    try:
        consumer.run()
    except KeyboardInterrupt:
        pass
    ch.queue_declare.assert_called_once_with(queue="newjob.queue", durable=False)
