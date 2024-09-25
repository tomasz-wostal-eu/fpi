import logging
import sys
from pythonjsonlogger import jsonlogger
import structlog
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base
from .crud import get_items, create_item, update_item, delete_item, get_item_by_id
from .schemas import Plant, PlantCreate
from . import schemas
from prometheus_client import start_http_server, Counter, Summary
import time
from fastapi import HTTPException


def configure_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

configure_logging()

app = FastAPI()

Base.metadata.create_all(bind=engine)

logger = structlog.get_logger()

# Create a metric to track time spent and requests made
REQUEST_TIME = Summary('fpi_request_processing_seconds', 'Time spent processing request')
REQUEST_COUNT = Counter('fpi_http_requests_total', 'Total number of HTTP requests')

# Start up the server to expose the metrics.
start_http_server(8001) 

@app.middleware("http")
async def add_prometheus_metrics(request, call_next):
    start_time = time.time()
    REQUEST_COUNT.inc()  # Increment the request count
    response = await call_next(request)
    request_latency = time.time() - start_time
    REQUEST_TIME.observe(request_latency)  # Record latency
    return response

@app.get("/metrics")
def get_metrics():
    return ""

@app.get("/healthcheck")
def liveness_probe():
    logger.info("Healthcheck")
    return "200"

@app.get("/plants/", response_model=list[Plant])
def read_plants(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    logger.info("Fetching plants", skip=skip, limit=limit)
    plants = get_items(skip=skip, limit=limit, db=db)
    return plants

@app.post("/plants/", response_model=Plant)
def add_plant(plant: PlantCreate, db: Session = Depends(get_db)):
    logger.info("Adding a new plant", plant=plant.model_dump())
    return create_item(plant, db=db)

@app.get("/plants/{plant_id}", response_model=Plant)
def read_plant(plant_id: int, db: Session = Depends(get_db)):
    logger.info("Fetching plant", plant_id=plant_id)
    plant = get_item_by_id(item_id=plant_id, db=db)
    if plant is None:
        logger.warning("Plant not found", plant_id=plant_id)
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant # pragma: no cover

@app.put("/plants/{plant_id}", response_model=Plant)
def update_plant(plant_id: int, plant: schemas.PlantUpdate, db: Session = Depends(get_db)):
    logger.info("Updating plant", plant_id=plant_id, update_data=plant.model_dump())
    updated_plant = update_item(item_id=plant_id, plant=plant, db=db)
    if updated_plant is None:
        logger.warning("Plant not found", plant_id=plant_id)
        raise HTTPException(status_code=404, detail="Plant not found")
    return updated_plant # pragma: no cover

@app.delete("/plants/{plant_id}", response_model=Plant)
def delete_plant(plant_id: int, db: Session = Depends(get_db)):
    logger.info("Deleting plant", plant_id=plant_id)
    deleted_plant = delete_item(item_id=plant_id, db=db)
    if deleted_plant is None:
        logger.warning("Plant not found", plant_id=plant_id)
        raise HTTPException(status_code=404, detail="Plant not found")
    return deleted_plant # pragma: no cover
