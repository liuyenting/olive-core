from pprint import pprint

import coloredlogs

from olive.core.managers.devices import Requirements
from olive.devices import AcustoOpticalModulator, LinearAxis


coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

requirements = Requirements()
requirements.update({"aotf": AcustoOpticalModulator})

print("** before")
for alias, device in requirements.items():
    print(f"{alias} -> {device}")
print()

for key, value in requirements.items():
    requirements[key] = 1

print("** after")
for alias, device in requirements.items():
    print(f"{alias} -> {device}")
print()

print("** satisfied?")
print(requirements.is_satisfied)
print()
