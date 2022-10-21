import pyvisa


class Keithley6487:
    """"
    Class for the keithley 6487 PicoAmmeter
    """
    def __init__(self):
        pass

    def set_voltage(self, voltage: float):
        pass

    def get_voltage(self,) -> float:
        pass

    def get_current(self) -> float:
        pass

    def set_current_range(self, limit: float) -> bool:
        pass

    def set_voltage_range(self, limit: float) -> bool:
        pass

    def voltage_on(self, ) -> bool:
        pass

    def voltage_off(self,) -> bool:
        pass

    def set_source_current_limit(self, limit: float) -> bool:
        pass

    def safe_shutdowm(self, ):
        # turn of voltage
        pass
