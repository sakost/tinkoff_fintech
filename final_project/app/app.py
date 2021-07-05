from fastapi import FastAPI

from .endpoints import router

app = FastAPI()
app.include_router(router)

if __name__ == '__main__':  # pragma: no cover
    from uvicorn import run

    run(app)
