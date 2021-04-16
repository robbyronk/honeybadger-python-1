import logging

from honeybadger import honeybadger
from starlette.requests import Request
from fastapi.routing import APIRoute
from typing import Callable
from . import asgi


class HoneybadgerRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            try:
                return await original_route_handler(request)
            except Exception as exc:
                try:
                    body = await request.json()
                except:
                    body = "error"
                scope = dict(request)
                scope["body"] = body
                honeybadger.notify(exception=exc, context=asgi._as_context(scope))
                raise exc from None
            finally:
                honeybadger.reset_context()
        return custom_route_handler
