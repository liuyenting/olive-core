import logging

from aiohttp.web import RouteTableDef, Response

__all__ = ["routes"]

logger = logging.getLogger(__name__)

routes = RouteTableDef()


@routes.get("/devices")
async def list_devices(request):
    print(f'GET /api/devices, "{request}"')

    response = Response()
    response.body = "Fuck this".encode()
    response.content_type = "text/plain"

    return response
