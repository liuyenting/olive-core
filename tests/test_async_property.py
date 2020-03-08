import asyncio
import functools
import logging
import typing
from dataclasses import dataclass
from collections import defaultdict

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


class DevicePropertyProxy:
    """
    Provide a proxy to access additional attributes.

    Args:
        coro (TBA): TBA
    """

    __slots__ = ("base", "instance")

    def __init__(self, base, instance):
        self.base = base
        self.instance = instance

    def __await__(self):
        # default await action is __get__
        return self.base.get_cache_value(self.instance).__await__()

    async def sync(self):
        await self.base.sync_cache_value(self.instance)


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

        # TODO attach sync to __get__

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
        return DevicePropertyProxy(self, instance)

    def __set__(self, instance, value):
        """
        Called to set the attribute on an instance of the owner class to a new value.

        Args:
            instance (object): the instance to operate on
            value : the new value
        """
        if self._fset is None:
            raise AttributeError("this property is not writable")
        self.set_cache_value(instance, value)

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

    def _get_instance_cache(self, instance):
        """Get cache collection."""
        try:
            return getattr(instance, DEVICE_PROPERTY_CACHE_ATTR)
        except AttributeError:
            # create the instance cache collection
            cache = dict()
            setattr(instance, DEVICE_PROPERTY_CACHE_ATTR, cache)
            return cache

    async def get_cache_value(self, instance):
        """
        Extract cache value from the cache attribute.

        Cache attribute is temporarily locked during the process to ensure reading is
        atomic.

        Args:
            instance (object): the instance to operate on
        """
        cache_collection = self._get_instance_cache(instance)
        name = self.__name__
        try:
            cache = cache_collection[name]
        except KeyError:
            logger.debug(f'"{name}" cache missed during get')
            value = await self._fget(instance)
            cache_collection[name] = DevicePropertyCache(value=value, dirty=False)
        else:
            async with cache.lock:
                if cache.dirty:
                    raise DirtyCacheError(f'"{name}" is not synchronized"')
                elif self._volatile:
                    logger.debug(f'"{name}" is volatile')
                    value = await self._fget(instance)
                    cache.value, cache.dirty = value, False  # explicit
                else:
                    # not dirty, not volatile
                    value = cache.value
        return value

    def set_cache_value(self, instance, value):
        """
        Store cache value to the cache attribute.

        When cache is modified, caller has to use `sync` to ensure cache is valid with the device.

        Args:
            instance (object): the instance to operate on
            value : the new value
        """
        cache_collection = self._get_instance_cache(instance)
        name = self.__name__
        try:
            cache = cache_collection[name]
        except KeyError:
            logger.debug(f'"{name}" cache missed during set')
            cache_collection[name] = DevicePropertyCache(value=value, dirty=True)
        else:
            cache.value, cache.dirty = value, True

    # TODO how to link sync when __get__
    async def sync_cache_value(self, instance):
        """Sync the device property with device."""
        cache_collection = self._get_instance_cache(instance)
        name = self.__name__
        # if we can call sync, cache already exists
        cache = cache_collection[name]
        async with cache.lock:
            if cache.dirty:
                logger.debug(f'"{name}" is dirty, synchronizing')
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
        self._val_1 = 0
        self._val_2 = 1

    @rw_property
    async def val1(self):
        print("getting val1")
        await asyncio.sleep(1)
        return self._val_1

    @val1.setter
    async def val1(self, new_val):
        print("setting val1")
        await asyncio.sleep(2)
        self._val_1 = new_val

    @rw_property
    async def val2(self):
        print("getting val2")
        await asyncio.sleep(1)
        return self._val_2

    @val2.setter
    async def val2(self, new_val):
        print("setting val2")
        await asyncio.sleep(2)
        self._val_2 = new_val


async def main():
    obj = MyObject()

    val = await obj.val1
    print(f"before, val1={val}")

    obj.val1 = 42
    await obj.val1.sync()

    val = await obj.val2
    print(f"after, val2={val}")

    val = await obj.val1
    print(f"after, val1={val}")


if __name__ == "__main__":
    import coloredlogs

    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )

    # launch generic loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
