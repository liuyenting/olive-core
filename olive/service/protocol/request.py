from dataclasses import dataclass
from enum import IntEnum


__all__ = []


class RequestMethod(IntEnum):
    POST = 1
    GET = 3
    PUT = 6
    DELETE = 8


class XRAPRequest(object):
    pass


class XRAPResponse(object):
    pass
