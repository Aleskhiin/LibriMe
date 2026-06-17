import asyncio
import base64
import json
import logging
import os
import threading

from fastapi import FastAPI, Request, Response
from google.cloud import pubsub_v1

from app_pkg.PubSub.PubSubJobHandler import PubSubJobHandler

logger = logging.getLogger(__name__)

app = FastAPI(title="LibriMe AI Module")

_handler: PubSubJobHandler | None = None
_subscriber_started = False


def _get_handler() -> PubSubJobHandler:
    global _handler
    if _handler is None:
        _handler = PubSubJobHandler()
    return _handler


@app.get("/")
def root():
    return {"status": "ok", "service": "LibriMe AI Module"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/pubsub/push")
async def pubsub_push(request: Request) -> Response:
    body = await request.json()
    loop = asyncio.get_running_loop()

    try:
        await loop.run_in_executor(None, _get_handler().handle, body)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Infrastructure error processing Pub/Sub push message: {e}", exc_info=True)
        return Response(status_code=500)


def _process_pull_message(message):
    try:
        logger.info(f"Received Pub/Sub message: {message.message_id}")

        msg = json.loads(message.data.decode("utf-8"))

        push_body = {
            "message": {
                "data": base64.b64encode(json.dumps(msg).encode("utf-8")).decode("utf-8")
            }
        }

        _get_handler().handle(push_body)

        message.ack()
        logger.info(f"Message {message.message_id} acknowledged")

    except Exception as e:
        logger.error(f"Error processing Pub/Sub pull message: {e}", exc_info=True)
        message.nack()


def _start_pull_subscriber():
    project_id = os.environ["PUBSUB_PROJECT_ID"]
    subscription_id = os.environ["PUBSUB_SUBSCRIPTION"]

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    logger.info(f"Listening on Pub/Sub subscription: {subscription_path}")

    future = subscriber.subscribe(subscription_path, callback=_process_pull_message)

    try:
        future.result()
    except Exception as e:
        logger.error(f"Pub/Sub subscriber stopped: {e}", exc_info=True)
        future.cancel()


@app.on_event("startup")
def startup_event():
    global _subscriber_started

    use_pull_worker = os.getenv("USE_PULL_WORKER", "true").lower() == "true"

    if not use_pull_worker:
        logger.info("Pull worker disabled. Only /pubsub/push endpoint is active.")
        return

    if _subscriber_started:
        return

    _subscriber_started = True

    thread = threading.Thread(target=_start_pull_subscriber, daemon=True)
    thread.start()

    logger.info("Pull worker background thread started.")