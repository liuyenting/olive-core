import asyncio
import functools
import logging
import typing
from dataclasses import dataclass

from olive.devices.error import DeviceError

DEVICE_PROPERTY_CACHE_ATTR = "__device_property_cache__"

logger = logging.getLogger(__name__)


class CacheError(DeviceError):
    pass


class CacheMiss(CacheError):
    pass


class DirtyCacheError(CacheError):
    pass


@dataclass
class DevicePropertyCache:
    value: typing.Any = None
    lock: asyncio.Lock = asyncio.Lock()
    dirty: bool = True


class DevicePropertyDescriptor:
    """
    This class builds a data descriptor that provides async read-write access for
    low-level hardwares, and annotate them with proper signatures.

    Args:
        fget
        fset
        volatile (bool, optional): property may change at any-time, access cache is not
            trustworthy
    """

    def __init__(self, fget=None, fset=None, volatile=False):
        self._fget, self._fset = fget, fset
        self._volatile = volatile

        # update wrapper using the getter/setter function
        functools.update_wrapper(self, fget if fget is not None else fset)

    def __get__(self, instance, owner=None):
        """
        Called to get the attribute of the owner class or of an instance of that class.

        Args:
            instance (object): the instance to operate on
            owner (object, optional): the owner class that acts as the proxy to operate
                on the instance
        """
        if instance is None:
            return self
        if self._fget is None:
            raise AttributeError("this property is not readable")
        return self._get_cache_value(instance)

    def __set__(self, instance, value):
        """
        Called to set the attribute on an instance of the owner class to a new value.

        Args:
            instance (object): the instance to operate on
            value : the new value
        """
        if self._fset is None:
            raise AttributeError("this property is not writable")
        self._set_cache_value(instance, value)
        # self._fset(instance, value)

    def __delete__(self, instance):
        raise AttributeError("device property is not deletable")

    ##
    # alternative constructor to attach setter

    def getter(self, fget):
        self._check_method_name(fget, self._fset, "getter")
        return type(self)(fget, self._fset, self._volatile)

    def setter(self, fset):
        self._check_method_name(fset, self._fget, "setter")
        return type(self)(self._fget, fset, self._volatile)

    def _check_method_name(self, new_method, current_method, method_type):
        assert (
            new_method.__name__ == current_method.__name__
        ), f"@{new_method.__name__}.{method_type} name must match property name"

    ##
    # cache access

    def _get_cache(self, instance):
        """Get cache attribute."""
        try:
            return getattr(instance, DEVICE_PROPERTY_CACHE_ATTR)
        except AttributeError:
            raise CacheMiss()
            logger.debug("cache missed, starts as dirty cache")
            cache = DevicePropertyCache(dirty=True)
            setattr(instance, DEVICE_PROPERTY_CACHE_ATTR, cache)
            return cache

    async def _get_cache_value(self, instance):
        """
        Extract cache value from the cache attribute.

        Cache attribute is temporarily locked during the process to ensure reading is
        atomic.

        Args:
            instance (object): the instance to operate on
        """
        try:
            cache = self._get_cache(instance)
        except CacheMiss:
            logger.debug(f"cache missed when getting {instance}")
            value = await self._fget(instance)
            cache = DevicePropertyCache(value=value, dirty=False)
            setattr(instance, DEVICE_PROPERTY_CACHE_ATTR, cache)
        else:
            # we might have not sync yet
            async with cache.lock:
                if cache.dirty:
                    raise DirtyCacheError()
                else:
                    value = cache.value
        return value

    def _set_cache_value(self, instance, value):
        """
        Store cache value to the cache attribute.

        When cache is modified, caller has to use `sync` to ensure cache is valid with the device.

        Args:
            instance (object): the instance to operate on
            value : the new value
        """
        try:
            cache = self._get_cache(instance)
            cache.value, cache.dirty = value, True
        except CacheMiss:
            logger.debug(f"cache missed when setting {instance}")
            cache = DevicePropertyCache(value=value, dirty=True)
            setattr(instance, DEVICE_PROPERTY_CACHE_ATTR, cache)

    # TODO how to link sync when __get__
    async def sync(self, instance):
        """Sync the device property with device."""
        cache = self._get_cache(instance)
        if cache.dirty:
            async with cache.lock:
                logger.debug("updating cache")
                await self._fset(instance, cache.value)
                cache.dirty = False


def rw_property(func, *args, **kwargs):
    """
    A readable and writable device property. You can annotate with getter and assign
    setter later, or vice versa.

    Args:
        func (TBA): TBA
    """
    assert asyncio.iscoroutinefunction(func), "can only use with async def"
    return DevicePropertyDescriptor(func, *args, **kwargs)


def ro_property():
    pass


def wo_property():
    pass


class MyObject(object):
    def __init__(self):
        self._val = 0

    @rw_property
    async def val(self):
        print("getting")
        await asyncio.sleep(1)
        return self._val

    @val.setter
    async def val(self, new_val):
        print("setting")
        await asyncio.sleep(2)
        self._val += new_val


async def main():
    obj = MyObject()

    val = await obj.val
    print(val)

    obj.val = 42
    val = await obj.val
    print(val)  # dirty cache exception

    print(dir(obj.val))


if __name__ == "__main__":
    import coloredlogs

    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )

    # launch generic loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
