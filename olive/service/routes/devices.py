import logging

from aiohttp.web import RouteTableDef, Response, json_response

__all__ = ["routes"]

logger = logging.getLogger(__name__)

routes = RouteTableDef()


@routes.get("/devices")
async def list_devices(request):
    print(f"GET devices")


@routes.get("/devices/host")
async def get_host_info(request):
    logger.debug(f"GET host_info")

    gateway = request.app["gateway"]

    hostname = gateway.query_hostname()

    return json_response({"hostname": hostname})


@routes.get("/devices/classes")
async def list_device_classes(request):
    print(f"GET device_classes")

