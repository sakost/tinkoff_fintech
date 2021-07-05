from fastapi import FastAPI

from .endpoints import router as endpoints_router
from .redis import router as redis_router
from .settings import settings

app = FastAPI(debug=settings.DEBUG)
app.include_router(redis_router)
app.include_router(endpoints_router)

if __name__ == '__main__':  # pragma: no cover
    from uvicorn import run

    run(app)
