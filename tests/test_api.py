import asyncio
import logging

import coloredlogs

from olive.service.app import launch

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    launch(port=7777)
