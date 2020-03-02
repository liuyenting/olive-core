import logging

from aiohttp.web import RouteTableDef, Response, json_response

__all__ = ["routes"]

logger = logging.getLogger(__name__)

routes = RouteTableDef()


@routes.get("/devices")
async def get_available_devices(request):
    try:
        uuid = request.app["gateway"].get_available_devices()
        return json_response(uuid, status=200)
    except KeyError:
        return Response(status=400, reason="invalid UUID")


@routes.get("/devices/classes")
async def get_available_device_classes(request):
    print(f"GET device_classes")


