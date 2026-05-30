import json
import pytest
from unittest.mock import Mock, AsyncMock, patch, ANY
from app_pkg.RabbitMQ.JobProcessor import make_job_callback, _lang_code, SPLITTING_MAP


def _make_connector():
    ch = Mock()
    conn = Mock()
    conn.channel.return_value = ch
    connector = Mock()
    connector.create_connection.return_value = conn
    return connector, ch


def _make_pika_args(body_dict: dict):
    ch = Mock()
    method = Mock()
    method.delivery_tag = 42
    props = Mock()
    body = json.dumps(body_dict).encode()
    return ch, method, props, body


def _base_msg(**overrides):
    msg = {
        "jobID": "test-uuid-1234",
        "fileLanguage": "en_US",
        "translationLanguage": "de_DE",
        "voiceID": "male_v1",
        "dataPath": "/opt/librime/files/test-uuid-1234/book.pdf",
        "splittingType": "DOCUMENT",
    }
    msg.update(overrides)
    return msg


def test_lang_code_strips_region():
    assert _lang_code("en_US") == "en"
    assert _lang_code("de_DE") == "de"


def test_splitting_map_covers_all_java_values():
    assert SPLITTING_MAP["DOCUMENT"] == "document"
    assert SPLITTING_MAP["PAGE"] == "pages"
    assert SPLITTING_MAP["PARAGRAPH"] == "paragraphs"


def test_callback_sends_running_then_completed_single_file():
    connector, prod_ch = _make_connector()
    pika_ch, method, props, body = _make_pika_args(_base_msg())

    with patch("app_pkg.RabbitMQ.JobProcessor.FeatureWorker") as MockFW:
        inst = Mock()
        MockFW.return_value = inst
        inst.run = AsyncMock(return_value={"audio": "/opt/librime/files/test-uuid-1234/test-uuid-1234.mp3"})

        make_job_callback(connector)(pika_ch, method, props, body)

    calls = prod_ch.basic_publish.call_args_list
    bodies = [json.loads(c[1]["body"]) for c in calls]

    assert len(bodies) == 2
    assert bodies[0] == {"jobID": "test-uuid-1234", "status": "RUNNING", "progress": 0, "resultPath": ""}
    assert bodies[1]["status"] == "COMPLETED"
    assert bodies[1]["progress"] == 100
    assert bodies[1]["resultPath"] == "/opt/librime/files/test-uuid-1234/test-uuid-1234.mp3"
    pika_ch.basic_ack.assert_called_once_with(delivery_tag=42)


def test_callback_sends_running_then_completed_multi_file():
    connector, prod_ch = _make_connector()
    pika_ch, method, props, body = _make_pika_args(_base_msg(splittingType="PAGE"))

    with patch("app_pkg.RabbitMQ.JobProcessor.FeatureWorker") as MockFW:
        inst = Mock()
        MockFW.return_value = inst
        inst.run = AsyncMock(return_value={
            "audios": [
                "/opt/librime/files/test-uuid-1234/test-uuid-1234_p1.mp3",
                "/opt/librime/files/test-uuid-1234/test-uuid-1234_p2.mp3",
            ]
        })

        make_job_callback(connector)(pika_ch, method, props, body)

    calls = prod_ch.basic_publish.call_args_list
    bodies = [json.loads(c[1]["body"]) for c in calls]

    assert bodies[-1]["status"] == "COMPLETED"
    assert bodies[-1]["resultPath"] == "/opt/librime/files/test-uuid-1234"
    pika_ch.basic_ack.assert_called_once_with(delivery_tag=42)


def test_callback_sends_failed_on_exception():
    connector, prod_ch = _make_connector()
    pika_ch, method, props, body = _make_pika_args(_base_msg())

    with patch("app_pkg.RabbitMQ.JobProcessor.FeatureWorker") as MockFW:
        inst = Mock()
        MockFW.return_value = inst
        inst.run = AsyncMock(side_effect=RuntimeError("TTS crashed"))

        make_job_callback(connector)(pika_ch, method, props, body)

    calls = prod_ch.basic_publish.call_args_list
    bodies = [json.loads(c[1]["body"]) for c in calls]

    assert bodies[0]["status"] == "RUNNING"
    assert bodies[-1] == {"jobID": "test-uuid-1234", "status": "FAILED", "progress": 0, "resultPath": ""}
    pika_ch.basic_ack.assert_called_once_with(delivery_tag=42)


def test_callback_maps_language_correctly():
    connector, _ = _make_connector()
    pika_ch, method, props, body = _make_pika_args(_base_msg(fileLanguage="de_DE", translationLanguage="en_US"))

    with patch("app_pkg.RabbitMQ.JobProcessor.FeatureWorker") as MockFW:
        inst = Mock()
        MockFW.return_value = inst
        inst.run = AsyncMock(return_value={"audio": "/opt/librime/files/test-uuid-1234/out.mp3"})

        make_job_callback(connector)(pika_ch, method, props, body)

        MockFW.assert_called_once_with(
            tts_output_dir="/opt/librime/files/test-uuid-1234",
            from_lang="de",
            to_lang="en",
        )


def test_callback_maps_splitting_type_to_read_mode():
    connector, _ = _make_connector()
    pika_ch, method, props, body = _make_pika_args(_base_msg(splittingType="PARAGRAPH"))

    with patch("app_pkg.RabbitMQ.JobProcessor.FeatureWorker") as MockFW:
        inst = Mock()
        MockFW.return_value = inst
        inst.run = AsyncMock(return_value={"audios": []})

        make_job_callback(connector)(pika_ch, method, props, body)

        inst.run.assert_called_once_with(
            input_file="/opt/librime/files/test-uuid-1234/book.pdf",
            read_mode="paragraphs",
            filename="test-uuid-1234",
        )
