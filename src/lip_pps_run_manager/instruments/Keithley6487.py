from lip_pps_run_manager.setup_manager import DeviceBase

from . import get_VISA_ResourceManager


class Keithley6487(DeviceBase):
    """
    Class for the keithley 6487 PicoAmmeter
    """

    _VISA_ResourceManager = None

    def __init__(self, device_name: str):
        super().__init__(device_name=device_name, device_type="Keithley6487")

        self._VISA_ResourceManager = get_VISA_ResourceManager()

    def set_voltage(self, voltage: float):
        pass

    def get_voltage(self) -> float:
        pass

    def get_current(self) -> float:
        pass

    def get_cv(self) -> float:
        pass

    def set_current_range(self, limit: float) -> bool:
        pass

    def set_voltage_range(self, limit: float) -> bool:
        pass

    def voltage_on(self) -> bool:
        pass

    def voltage_off(self) -> bool:
        pass

    def set_source_current_limit(self, limit: float) -> bool:
        pass

    def safe_shutdowm(self):
        pass
