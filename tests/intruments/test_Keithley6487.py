from unittest.mock import patch

from test_functions import ReplaceResourceManager

from lip_pps_run_manager.instruments import Keithley6487
from lip_pps_run_manager.setup_manager import DeviceBase


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_type():
    assert issubclass(Keithley6487, DeviceBase)

    instrument = Keithley6487("myName")

    assert isinstance(instrument, DeviceBase)
    assert isinstance(instrument, Keithley6487)
