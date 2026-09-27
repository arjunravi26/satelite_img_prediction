from fastapi import Request
from src.service.service import Service


def get_service(request: Request) -> Service:
    return request.app.state.service