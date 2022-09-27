from pathlib import Path

import lip_pps_run_manager as RM
from lip_pps_run_manager.cli import main


def test_main():
    main([])


def test_run_manager():
    John = RM.RunManager(Path("./Run0001"))
    assert John.path_directory == Path("./Run0001")
    assert John.run_name == "Run0001"


def test_fail_run_manager():
    try:
        RM.RunManager(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_run_directory` must be a Path type object, received object of type <class 'str'>")
