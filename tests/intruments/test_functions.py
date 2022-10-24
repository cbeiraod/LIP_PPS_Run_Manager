from unittest.mock import patch

from lip_pps_run_manager.instruments import functions


class ReplaceResourceManager:
    pass


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_get_resource_manager():
    import pyvisa

    value = functions.get_VISA_ResourceManager()

    assert isinstance(value, pyvisa.ResourceManager)
