import importlib
import pkgutil
from pprint import pprint

import olive.drivers


def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


drivers = {
    name: importlib.import_module(name)
    for finder, name, ispkg in iter_namespace(olive.drivers)
}
pprint(drivers)

for name, module in drivers.items():
    print()
    print(name)
    pprint(module.__dict__['__all__'])
