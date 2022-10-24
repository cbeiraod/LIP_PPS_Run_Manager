from unittest.mock import patch

from lip_pps_run_manager.instruments import functions


class ReplaceResourceManager:
    def __init__(self):
        pass

    def open_resource(self, string):
        self._resource_string = string

        return self


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_get_resource_manager():
    import pyvisa

    value = functions.get_VISA_ResourceManager()

    assert isinstance(value, pyvisa.ResourceManager)
