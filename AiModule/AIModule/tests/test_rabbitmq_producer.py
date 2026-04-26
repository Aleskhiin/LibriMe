import json
import pytest
from unittest.mock import Mock, ANY
from app_pkg.RabbitMQ.RabbitMQProducer import RabbitMQProducer


def _make_connector():
    ch = Mock()
    conn = Mock()
    conn.channel.return_value = ch
    connector = Mock()
    connector.create_connection.return_value = conn
    return connector, ch, conn


def test_publish_uses_correct_exchange_and_routing_key():
    connector, ch, _ = _make_connector()
    producer = RabbitMQProducer(connector)
    producer.publish({"jobID": "abc", "status": "RUNNING", "progress": 0, "resultPath": ""})
    ch.basic_publish.assert_called_once_with(
        exchange="job.exchange",
        routing_key="donejob.key",
        body=ANY,
        properties=ANY,
    )


def test_publish_serialises_dict_to_json():
    connector, ch, _ = _make_connector()
    producer = RabbitMQProducer(connector)
    msg = {"jobID": "abc", "status": "COMPLETED", "progress": 100, "resultPath": "/opt/librime/files/abc/abc.mp3"}
    producer.publish(msg)
    actual_body = ch.basic_publish.call_args[1]["body"]
    assert json.loads(actual_body) == msg


def test_close_closes_connection():
    connector, _, conn = _make_connector()
    producer = RabbitMQProducer(connector)
    producer.close()
    conn.close.assert_called_once()


def test_init_does_not_declare_queue():
    connector, ch, _ = _make_connector()
    RabbitMQProducer(connector)
    ch.queue_declare.assert_not_called()
