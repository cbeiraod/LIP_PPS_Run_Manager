class DeviceBase:
    """This is the base class for implementing a device for an experimental setup"""

    _type = None
    _name = None

    def __init__(self, device_name: str, device_type: str):
        self._type = device_type
        self._name = device_name

    def safe_shutdown(self):
        raise RuntimeError("The device type {} has not had its safe shutdown set...".format(self._type))  # pragma: no cover


class VISADevice(DeviceBase):
    """This is the base class for implementing a device for an experimental setup which communicates with the VISA interface"""

    _VISA_ResourceManager = None
    _VISA_Handle = None
    _resource_string = None

    def __init__(self, device_type: str, device_name: str, resource_string: str):
        super().__init__(device_name=device_name, device_type=device_type)
        self._resource_string = resource_string

        from .instruments import get_VISA_ResourceManager

        self._VISA_ResourceManager = get_VISA_ResourceManager()

        self._VISA_Handle = self._VISA_ResourceManager.open_resource(resource_string)


class SetupManager:
    """This class holds details about the experimental setup (particularly useful for device configuration)"""

    _devices = {}

    def __init__(self):
        pass  # pragma: no cover
        # Still under construction
