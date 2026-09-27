from fastapi import FastAPI
from api.v1.predict_router import predict_router
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from src.service.service import Service


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = Service()
    print("Model loaded successfully into app.state")
    yield
    if hasattr(app.state, "service"):
        app.state.service.db.close()
        del app.state.service


app = FastAPI(lifespan=lifespan)
app.include_router(predict_router)


@app.get("/")
async def main():
    content = f"""
        <body>
        <form action="/predict/" enctype="multipart/form-data" method="post">
        <input name="file" type="file" multiple>
        <input type="submit">
        </form>
        </body>
    """
    return HTMLResponse(content=content)
