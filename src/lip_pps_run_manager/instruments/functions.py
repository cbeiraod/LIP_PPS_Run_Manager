import pyvisa

VISARM = None


def get_VISA_ResourceManager():
    global VISARM

    if VISARM is None:
        VISARM = pyvisa.ResourceManager()

    return VISARM
