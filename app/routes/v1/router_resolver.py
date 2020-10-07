from fastapi import APIRouter
from util import Singleton


class RouterResolver(metaclass=Singleton):
    def __init__(self):
        self._router = APIRouter()

    @property
    def router(self) -> APIRouter:
        return self._router
