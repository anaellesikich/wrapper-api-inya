import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .utils.logging import setup_logging
from .routes.v1 import generate as gen_v1
from .routes.v1 import health as health_v1
from .routes.v1 import docs as docs_v1


setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid, time
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    latency = int((time.perf_counter() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info(f"request_complete path={request.url.path} status={response.status_code} latency_ms={latency} request_id={request_id}")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception")
    return JSONResponse(status_code=500, content={"error": "Internal server error", "path": request.url.path})

app.include_router(health_v1.router, prefix="/v1", tags=["health"])
app.include_router(gen_v1.router, prefix="/v1", tags=["generate"])
app.include_router(docs_v1.router, prefix="/v1/docs", tags=["docs"])


@app.get("/")
async def root():
    return {"service": settings.APP_NAME, "version": "v1"}
