import asyncio
import logging

from fastapi import FastAPI, Request, Response

from app_pkg.PubSub.PubSubJobHandler import PubSubJobHandler

logger = logging.getLogger(__name__)

app = FastAPI(title="LibriMe AI Module")

_handler: PubSubJobHandler | None = None


def _get_handler() -> PubSubJobHandler:
    global _handler
    if _handler is None:
        _handler = PubSubJobHandler()
    return _handler


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
        logger.error(f"Infrastructure error processing Pub/Sub message: {e}")
        return Response(status_code=500)
