import os
import yaml

from app_pkg.RabbitMQ.RabbitMQConnector import RabbitMQConnector
from app_pkg.RabbitMQ.RabbitMQManager import RabbitMQManager
from app_pkg.RabbitMQ.JobProcessor import make_job_callback

CONSUMER_QUEUE = "newjob.queue"


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "app_pkg", "Resources", "config.yaml")
    config = load_config(config_path)

    host = os.environ.get("RABBITMQ_HOST") or config["rabbitmq"]["host"]
    num_workers = config["rabbitmq"].get("num_workers", 2)

    connector = RabbitMQConnector(host=host)
    manager = RabbitMQManager(connector)
    callback = make_job_callback(connector)
    manager.add_consumer(CONSUMER_QUEUE, callback, count=num_workers)

    print(f"[*] LibriMe AI Module starting — {num_workers} worker(s) on '{CONSUMER_QUEUE}'")
    manager.start_all()
    manager.wait_for_all()
