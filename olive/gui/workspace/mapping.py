from enum import IntEnum, auto
from collections import namedtuple

from .device_hub import DeviceHubPresenter, DeviceHubView

__all__ = ["Workspace", "workspace_defs"]


class Workspace(IntEnum):
    DeviceHub = auto()  # 1)
    ProtocolEditor = auto()  # 2)
    Acquisition = auto()  # 3)


# class definition for each workspaces
WorkspaceClass = namedtuple("WorkspaceClass", ["presenter", "view"])
workspace_defs = {
    # Workspace.Acquisition: WorkspaceClass(None, None),
    Workspace.DeviceHub: WorkspaceClass(DeviceHubPresenter, DeviceHubView),
    # Workspace.ProtocolEditor: WorkspaceClass(None, None),
}

