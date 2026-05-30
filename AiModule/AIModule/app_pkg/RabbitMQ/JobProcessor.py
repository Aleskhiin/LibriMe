import asyncio
import json
import os

from app_pkg.FeatureWorker import FeatureWorker
from app_pkg.RabbitMQ.RabbitMQProducer import RabbitMQProducer

SPLITTING_MAP = {
    "DOCUMENT": "document",
    "PAGE": "pages",
    "PARAGRAPH": "paragraphs",
}


def _lang_code(lang_type: str) -> str:
    return lang_type.split("_")[0]


def make_job_callback(connector):
    def callback(ch, method, properties, body):
        msg = json.loads(body)
        job_id = msg["jobID"]
        data_path = msg["dataPath"]
        from_lang = _lang_code(msg["fileLanguage"])
        to_lang = _lang_code(msg["translationLanguage"])
        read_mode = SPLITTING_MAP.get(msg["splittingType"], "document")
        uuid_dir = os.path.dirname(data_path)

        producer = RabbitMQProducer(connector)
        try:
            producer.publish({"jobID": job_id, "status": "RUNNING", "progress": 0, "resultPath": ""})

            worker = FeatureWorker(tts_output_dir=uuid_dir, from_lang=from_lang, to_lang=to_lang)
            result = asyncio.run(worker.run(input_file=data_path, read_mode=read_mode, filename=job_id))

            if "audio" in result:
                result_path = result["audio"]
            else:
                result_path = uuid_dir

            producer.publish({"jobID": job_id, "status": "COMPLETED", "progress": 100, "resultPath": result_path})
        except Exception:
            producer.publish({"jobID": job_id, "status": "FAILED", "progress": 0, "resultPath": ""})
        finally:
            producer.close()
            ch.basic_ack(delivery_tag=method.delivery_tag)

    return callback
