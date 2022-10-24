class DeviceBase:
    """This is the base class for implementing a device for an experimental setup"""

    _type = None
    _name = None

    def __init__(self, device_name: str, device_type: str):
        self._type = device_type
        self._name = device_name

    def safe_shutdown(self):
        raise RuntimeError("The device type {} has not had its safe shutdown set...".format(self._type))


class SetupManager:
    """This class holds details about the experimental setup (particularly useful for device configuration)"""

    _devices = {}

    def __init__(self):
        pass
