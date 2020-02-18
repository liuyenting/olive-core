import asyncio
import logging

import coloredlogs
import serial_asyncio

from olive.drivers.utils import SerialPortManager

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


async def main():
    serial_manager = SerialPortManager()
    print(serial_manager.list_ports())

    try:
        port = await asyncio.wait_for(serial_manager.request_port("COM1"), timeout=5)
    except asyncio.TimeoutError:
        logger.error("timeout")
        return

    loop = asyncio.get_running_loop()
    reader, writer = await serial_asyncio.open_serial_connection(
        loop=loop, url=port, baudrate=19200
    )

    logger.info("writing")
    writer.write("\r".encode())
    await writer.drain()

    logger.info("reading")
    try:
        data = await asyncio.wait_for(reader.readuntil("?".encode()), timeout=5)
    except asyncio.TimeoutError:
        logger.error("read timeout")
    else:
        data = data.decode()
        print(data)

    serial_manager.release_port(port)


if __name__ == "__main__":
    asyncio.run(main())
