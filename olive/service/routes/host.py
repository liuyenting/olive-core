import logging

from aiohttp.web import RouteTableDef, Response, json_response

__all__ = ["routes"]

logger = logging.getLogger(__name__)

routes = RouteTableDef()


@routes.get("/host/hostname")
async def get_hostname(request):
    hostname = request.app["gateway"].query_hostname()
    return Response(status=200, text=hostname)
