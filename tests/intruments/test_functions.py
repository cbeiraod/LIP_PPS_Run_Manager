from unittest.mock import patch

from lip_pps_run_manager.instruments import functions


class ReplaceResource:
    def __init__(self, name):
        self._name = name
        self._history = []
        self._return_message = ""

    def _get_history(self):
        return self._history

    def _set_return_message(self, message):
        self._return_message = message

    def write(self, query):
        self._history += [query]

    def query(self, query):
        self._history += [query]

        return self._return_message

    def read(self):
        return self._return_message


class ReplaceResourceManager:
    def __init__(self):
        pass

    def open_resource(self, string):
        self._resource_string = string

        return ReplaceResource(string)


@patch('pyvisa.ResourceManager', new=ReplaceResourceManager)  # To avoid sending actual VISA requests
def test_get_resource_manager():
    import pyvisa

    value = functions.get_VISA_ResourceManager()

    assert isinstance(value, pyvisa.ResourceManager)
