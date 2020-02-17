import coloredlogs

from olive.ui.launcher import launch

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

if __name__ == "__main__":
    launch()
