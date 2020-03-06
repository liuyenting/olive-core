import functools
import asyncio
from dataclasses import dataclass
import typing

ASYNC_PROPERTY_ATTR = "__device_property_cache__"


@dataclass
class DevicePropertyCache:
    cache: typing.Any = None
    lock: asyncio.Lock = asyncio.Lock()
    dirty: bool = False


class DevicePropertyDescriptor:
    """
    This class builds a data descriptor that provides async read-write access for
    low-level hardwares, and annotate them with proper signatures.
    """

    def __init__(self, fget=None, fset=None, doc=None):
        self._fget, self._fset = fget, fset

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
        return self._fget(instance)

    def __set__(self, instance, value):
        """
        Called to set the attribute on an instance of the owner class to a new value.

        Args:
            instance (object): the instance to operate on
            value : the new value
        """
        if self._fset is None:
            raise AttributeError("this property is not writable")
        self._fset(instance, value)

    def __delete__(self, instance):
        raise AttributeError("device property is not deletable")

    ##
    # alternative constructors

    def getter(self, fget):
        return type(self)(fget, self._fset, self.__doc__)

    def setter(self, fset):
        return type(self)(self._fget, fset, self.__doc__)

    ##
    #

    async def sync(self):
        """Sync the property with device."""
        # TODO trigger fset
        pass


class ReadOnlyDevicePropertyDescriptor(DevicePropertyDescriptor):
    pass


class WriteOnlyDevicePropertyDescriptor(DevicePropertyDescriptor):
    pass


def device_property(func, *args, **kwargs):
    assert asyncio.iscoroutinefunction(func), "can only use with async def"
    return DevicePropertyDescriptor(func, *args, **kwargs)


class MyObject(object):
    def __init__(self):
        self.val = 0

    @device_property
    async def val(self):
        print("getting")
        await asyncio.sleep(1)
        return self.val

    @val.setter
    async def val(self, new_val):
        print("setting")
        await asyncio.sleep(1)
        # self.val += new_val


async def main():
    obj = MyObject()
    val = await obj.val
    print(val)


if __name__ == "__main__":
    # launch generic loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
