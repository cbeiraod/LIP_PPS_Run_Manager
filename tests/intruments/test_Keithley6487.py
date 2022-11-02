from unittest.mock import patch

from test_functions import ReplaceResourceManager

from lip_pps_run_manager.instruments import Keithley6487
from lip_pps_run_manager.setup_manager import DeviceBase


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_type():
    assert issubclass(Keithley6487, DeviceBase)

    instrument = Keithley6487("myName", "Resource String")

    assert isinstance(instrument, DeviceBase)
    assert isinstance(instrument, Keithley6487)


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_set_id():
    instrument = Keithley6487("myName", "Resource String")

    query_hist = instrument._VISA_Handle._get_history()

    assert "*IDN?" == query_hist[0]


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_set_voltage():
    instrument = Keithley6487("myName", "Resource String")

    instrument.set_voltage(20)

    query_hist = instrument._VISA_Handle._get_history()

    assert "SOURCE:VOLTAGE 20" == query_hist[1]


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_set_voltage_bad_type():
    instrument = Keithley6487("myName", "Resource String")

    try:
        instrument.set_voltage("20")
    except TypeError as e:
        assert str(e) == ""
