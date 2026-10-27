import logging

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/hello")
def hello():
    logger.info("Endpoint /hello called")
    return {"message": "Backend response!", "version": "1.0"}
