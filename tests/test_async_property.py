import asyncio

from olive.devices import ro_property, rw_property, wo_property, DevicePropertyDataType


class MyObject(object):
    def __init__(self):
        self._val_1 = 10
        self._val_2 = 20
        self._val_3 = 30

    @rw_property(dtype=DevicePropertyDataType.Integer, volatile=False, min=5)
    async def val1(self):
        print("getting val1")
        await asyncio.sleep(1)
        return self._val_1

    @val1.setter
    async def val1(self, new_val):
        print("setting val1")
        await asyncio.sleep(2)
        self._val_1 = new_val

    @rw_property(dtype=DevicePropertyDataType.Integer, volatile=True, min=-5)
    async def val2(self):
        print("getting val2")
        await asyncio.sleep(1)
        return self._val_2

    """
    @val2.setter
    async def val2(self, new_val):
        print("setting val2")
        await asyncio.sleep(2)
        self._val_2 = new_val
    """

    @wo_property(dtype=DevicePropertyDataType.Integer)
    async def val3(self, new_val):
        print("setting val3")
        await asyncio.sleep(1)
        self._val_3 = new_val


class MyInheritObject(MyObject):
    def __init__(self):
        super().__init__()
        self._val_4 = 40

    @ro_property(dtype=DevicePropertyDataType.Integer)
    async def val4(self):
        return self._val_4


class MyChildObject:
    def __init__(self, parent):
        self.parent = parent
        self._val_5 = 50

    def __getattr__(self, name):
        return getattr(self.parent, name)

    ##

    @ro_property(dtype=DevicePropertyDataType.Integer)
    async def val5(self):
        return self._val_5


async def main2():
    obj1 = MyInheritObject()

    print(obj1.val1.min)
    print(obj1.val2.max)

    obj1.val1 = 42
    await obj1.val1.sync()

    for _ in range(3):
        print(f'val1={await obj1.val1}')
        print(f'val2={await obj1.val2}')


async def main():
    obj = MyInheritObject()

    val = await obj.val1
    print(f"before, val1={val}")

    print(obj.val1)
    obj.val1 = 42
    print(obj.val1)
    await obj.val1.sync()

    val = await obj.val2
    print(f"after, val2={val}")

    # obj.val2 = 42

    val = await obj.val1
    print(f"after, val1={val}")

    val = await obj.val2
    print(f"after, val2={val}")

    """
    val = await obj.val3
    print("val3 read")
    """

    obj.val3 = 42
    await obj.val3.sync()
    print(f"after, val3 synced")

    # val = await obj.val3

    val = await obj.val4
    print(f"inherit, val4={val}")


if __name__ == "__main__":
    import coloredlogs

    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )

    # launch generic loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main2())
