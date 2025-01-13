from typing import List

from fastapi import APIRouter, FastAPI

from src.server.routes.participants_routes import participants_router
from src.server.routes.utility_routes import utility_router
from src.server.routes.teams_routes import teams_router
from src.server.routes.verification_routes import verification_router


class Routes:
    _routers: List[APIRouter] = [utility_router, participants_router, teams_router, verification_router]
    """For every part of our system we create a separate router. In order for a router to be visible we should add it
    to the list"""

    @classmethod
    def register_routes(cls, app: FastAPI) -> None:
        for router in cls._routers:
            app.include_router(router)
