import asyncio
import logging
from pprint import pprint

import coloredlogs
from serial.tools import list_ports
import serial_asyncio

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


async def main():
    ports = [port.device for port in list_ports.comports()]
    print(ports)

    loop = asyncio.get_running_loop()
    reader, writer = await serial_asyncio.open_serial_connection(
        loop=loop, url="COM12", baudrate=57600
    )

    writer.write("\r".encode())
    await writer.drain()

    data = await reader.readuntil("?".encode())
    data = data.decode()

    print(data)


if __name__ == "__main__":
    asyncio.run(main())
