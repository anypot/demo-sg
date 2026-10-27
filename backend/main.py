from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/hello")
def hello():
    logger.info("Endpoint /hello called")
    return {"message": "Backend response!"}
