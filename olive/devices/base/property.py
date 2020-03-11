from __future__ import annotations

import asyncio
import functools
import logging
import sys
import typing
from dataclasses import dataclass
from enum import IntEnum, auto

from ..error import DirtyPropertyCacheError

__all__ = [
    "ro_property",
    "wo_property",
    "rw_property",
    "DevicePropertyDataType",
    "DEVICE_PROPERTY_CACHE_ATTR",
]

DEVICE_PROPERTY_CACHE_ATTR = "__device_property_cache__"

logger = logging.getLogger("olive.devices.property")


class DevicePropertyDataType(IntEnum):
    Integer = auto()
    Float = auto()
    Enum = auto()
    Array = auto()


@dataclass
class DevicePropertyCache:
    value: typing.Any
    lock: asyncio.Lock = asyncio.Lock()
    dirty: bool = True


class DevicePropertyDescriptorProxy:
    """
    Provide a proxy to access additional attributes.

    Args:
        base (DevicePropertyDescriptor): the descriptor
        instance (object): the instance to operate on
    """

    __slots__ = ("base", "instance")

    def __init__(self, base: DevicePropertyDescriptor, instance):
        self.base = base
        self.instance = instance

    def __await__(self):
        # default await action
        return self.base._get_cache_value(self.instance).__await__()

    def __getattr__(self, name):
        # device property proxy only needs to delegate methods to the descriptor class
        attr = getattr(self.base, name)
        if isinstance(getattr(type(self.base), name), property):
            # properties are not instance dependent
            #
            # Determine if given class attribute is a property or not, Python object
            #   https://stackoverflow.com/a/17735716
            return attr
        else:
            # rest of the functions require cache, which is dependent on instances
            return functools.partial(attr, self.instance)


class DevicePropertyDescriptor:
    """
    This class builds a data descriptor that provides async read-write access for
    low-level hardwares, and annotate them with proper signatures.

    Args:
        fget : getter function
        fset : setter function
        **attrs (dict, optional): additional parameters can be assigned to define the
            value range, possible combinations:
                - 'dtype' -> str: ['integer', 'float', 'enum', 'array']

                - for every dtype:
                    - 'default': default value
                    - 'unit' -> str: unit of the data
                    - 'volatile' -> bool: cache is not trustworthy

                - for 'integer':
                    - 'min' -> int: minimumn
                    - 'max' -> int: maximum
                    - 'step' -> int: steps between valid values

                - for 'float':
                    - 'min' -> float: minimumn
                    - 'max' -> float: maximum
                    - 'step' -> float: steps between valid values

                - for 'enum':
                    - 'enum' -> Enum: the enum class

                - for 'array':
                    - 'nelem' -> int: number of elements in the array
                    - 'elem_dtype' -> str: element data type, same as 'dtype'
                    - attributes that accompany the element data type

    Note:
        Unused attributes are _undefined_, their values are meaningless.
    """

    def __init__(self, dtype: DevicePropertyDataType, fget=None, fset=None, **attrs):
        # sync wrapper to accessor info
        template = fget if fget is not None else fset  # fget takes precedence
        functools.update_wrapper(self, template)

        self._fget, self._fset = fget, fset
        self._validate_func_type()

        # property attributes
        self._dtype, self._attrs = dtype, attrs
        self._validate_data_info()

    def _validate_func_type(self):
        """
        Device property descriptor is intended to work as an modified async property
        descriptor class. Therefore, its wrapped function should be coroutines.
        """
        if self._fget is not None:
            assert asyncio.iscoroutinefunction(
                self._fget
            ), f"{self.__name__}.getter is not a coroutine"
        if self._fset is not None:
            assert asyncio.iscoroutinefunction(
                self._fset
            ), f"{self.__name__}.setter is not a coroutine"

    def _validate_data_info(self):
        """Validate whether attribute arguments contain sufficient info."""
        dtype, attrs = self._dtype, self._attrs

        # common property attributes
        attrs.setdefault("volatile", False)
        attrs.setdefault("unit", "")

        if dtype == DevicePropertyDataType.Integer:
            attrs.setdefault("min", -sys.maxsize - 1)
            attrs.setdefault("max", sys.maxsize)
            attrs.setdefault("step", 1)
            attrs.setdefault("default", 0)
        elif dtype == DevicePropertyDataType.Float:
            attrs.setdefault("min", sys.float_info.min)
            attrs.setdefault("max", sys.float_info.max)
            attrs.setdefault("step", sys.float_info.epsilon)
            attrs.setdefault("default", 0)
        elif dtype == DevicePropertyDataType.Enum:
            assert all(
                attr in attrs for attr in ("enum", "default")
            ), "incomplete enum definition"
        elif dtype == DevicePropertyDataType.Array:
            assert all(
                attr in attrs for attr in ("nelem", "elem_dtype", "default")
            ), "incomplete info for array type"
            # validate element type info
            self._validate_data_info(attrs["elem_dtype"], attrs)

    def __get__(self, instance, owner=None):
        """
        Called to get the attribute of the owner class or of an instance of that class.

        Naive implementation of descriptor objects, such that descriptor class itself
        stores the values, this may cause multiple instances of the same class to
        override the values store in the descriptor instance. Therefore, we have to
        access cache values from the instance attribute.

        Args:
            instance (object): the instance to operate on
            owner (object, optional): the owner class that acts as the proxy to operate
                on the instance
        """
        if instance is None:
            return self
        return DevicePropertyDescriptorProxy(self, instance)

    def __set__(self, instance, value):
        """
        Called to set the attribute on an instance of the owner class to a new value.

        Args:
            instance (object): the instance to operate on
            value : the new value
        """
        assert self._fset is not None, f"{self.__name__}.setter not implemented"
        self._set_cache_value(instance, value)

    def __delete__(self, instance):
        raise AttributeError(f'"{self.__name__}" is not deletable')

    ##
    # alternative constructor to attach accessor

    def _check_method_name(self, new_method, current_method, method_type):
        assert (
            new_method.__name__ == current_method.__name__
        ), f"@{new_method.__name__}.{method_type} name must match property name"

    ##
    # cache access

    def _get_instance_cache(self, instance):
        """
        Get cache collection of an instance.

        All the cached properties are stored in DEVICE_PROPERTY_CACHE_ATTR, in order to
        keep the descriptor class and its clients decoupled.

        Args:
            instance (object): the instance to operate on
        """
        try:
            return getattr(instance, DEVICE_PROPERTY_CACHE_ATTR)
        except AttributeError:
            # create the instance cache collection
            cache = dict()
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
                    raise DirtyPropertyCacheError(f'"{name}" is not synchronized"')
                elif self.volatile:
                    logger.debug(f'"{name}" is volatile')
                    value = await self._fget(instance)
                    cache.value, cache.dirty = value, False  # explicit
                else:
                    # not dirty, not volatile
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
        cache_collection = self._get_instance_cache(instance)
        name = self.__name__
        try:
            cache = cache_collection[name]
        except KeyError:
            logger.debug(f'"{name}" cache missed during set')
            cache_collection[name] = DevicePropertyCache(value=value, dirty=True)
        else:
            cache.value, cache.dirty = value, True

    async def sync(self, instance):
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

    ##
    # value type

    @property
    def dtype(self) -> DevicePropertyDataType:
        """
        enum, integer, float, array
        """
        return self._dtype

    @property
    def volatile(self) -> bool:
        """Property may change at any-time, access cache is not trustworthy."""
        return self._attrs["volatile"]

    @property
    def unit(self) -> str:
        """Unit of the property."""
        return self._attrs["unit"]

    @property
    def default(self):
        return self._attrs["default"]

    ##
    # value type - numeric

    @property
    def min(self):
        return self._attrs["min"]

    @property
    def max(self):
        return self._attrs["max"]

    @property
    def step(self):
        return self._attrs["step"]

    ##
    # value type - enum

    @property
    def enum(self):
        return self._attrs["enum"]

    ##
    # value type - enum

    @property
    def nelem(self) -> int:
        """Number of elements in the array."""
        return self._attrs["nelem"]

    @property
    def elem_dtype(self) -> DevicePropertyDataType:
        """Data type of array elements."""
        return self._attrs["elem_dtype"]


class rw_property(DevicePropertyDescriptor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, fget):
        """RW property direct descriptor call is always on fget."""
        return type(self)(dtype=self._dtype, fget=fget, fset=self._fset, **self._attrs)

    ##
    # alternative constructor to attach accessor

    def setter(self, fset):
        self._check_method_name(fset, self._fget, "setter")
        return type(self)(dtype=self._dtype, fget=self._fget, fset=fset, **self._attrs)


class ro_property(rw_property):
    """
    Read-only device property.

    Args:
        func (TBA): TBA
    """

    ##
    # disable setters

    def __set__(self, instance, value):
        raise AttributeError(f'"{self.__name__}" is read-only')

    def setter(self, fset):
        raise AttributeError(f'"{self.__name__}" is read-only')


class wo_property(DevicePropertyDescriptor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, fset):
        """WO property direct descriptor call is always on fset."""
        return type(self)(dtype=self._dtype, fset=fset, **self._attrs)

    ##
    # disable getters

    async def _get_cache_value(self, instance):
        raise AttributeError(f'"{self.__name__}" is write-only')

