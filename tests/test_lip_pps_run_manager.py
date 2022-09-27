from pathlib import Path

import lip_pps_run_manager as RM
from lip_pps_run_manager.cli import main


def test_main():
    main([])


def test_run_manager():
    John = RM.RunManager(Path("."))
    assert John.path_storage == Path(".")


def test_fail_run_manager():
    try:
        RM.RunManager(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_run_storage` must be a Path type object, received object of type <class 'str'>")
