import logging

from aiohttp.web import RouteTableDef, Response, json_response

__all__ = ["routes"]

logger = logging.getLogger(__name__)

routes = RouteTableDef()


@routes.get("/host/{key}")
async def get_host_info(request):
    logger.debug(f"GET host_info")

    gateway = request.app["gateway"]
    key = request.match_info["key"]

    func_mapping = {"hostname": gateway.query_hostname}
    try:
        func = func_mapping[key]
        value = func()
        # TODO wrap http json response
    except KeyError:
        # TODO get everything if key is empty
        # TODO send http error
        pass
    hostname = gateway.query_hostname()

    return json_response({"hostname": hostname})
