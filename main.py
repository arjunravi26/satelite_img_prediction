from fastapi import FastAPI
from api.v1.predict_router import predict_router
from api.v1.query_router import query_router
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from src.service.service import Service
from design import pred_design_html, query_design_html


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
app.include_router(query_router)


@app.get("/")
async def main():
    return HTMLResponse(content=pred_design_html)


@app.get("/query")
async def analyst_page():
    return HTMLResponse(content=query_design_html)
