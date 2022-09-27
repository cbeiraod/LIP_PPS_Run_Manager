import shutil
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


def test_run_exists_function():
    runName = "hopefully_unique_run_name"
    p = Path(".") / runName
    p.mkdir(exist_ok=True)
    (p / 'run_info.txt').touch()
    assert RM.run_exists(Path("."), runName)  # Test when exists
    shutil.rmtree(p)
    assert not RM.run_exists(Path("."), runName)  # Test when doesn't exist


def test_fail_run_exists_function():
    try:
        RM.run_exists(".", "a")
    except TypeError as e:
        assert str(e) == ("The `path_to_directory` must be a Path type object, received object of type <class 'str'>")

    try:
        RM.run_exists(Path("."), 2)
    except TypeError as e:
        assert str(e) == ("The `run_name` must be a str type object, received object of type <class 'int'>")


def test_clean_path_function():
    assert isinstance(RM.clean_path(Path(".")), Path)  # Test return type
    # TODO: assert RM.clean_path(Path("./Run@2")) == Path("./Run2") # Test actual cleaning


def test_fail_clean_path_function():
    try:
        RM.clean_path(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_clean` must be a Path type object, received object of type <class 'str'>")


def test_create_run_function():
    basePath = Path("/tmp")
    runName = "testRun_21"

    assert RM.create_run(basePath, runName) == basePath / runName
    assert (basePath / runName).is_dir()
    assert (basePath / runName / "run_info.txt").is_file()
    # TODO: Check contents of run_info.txt file
    shutil.rmtree(basePath / runName)
    assert not (basePath / runName).is_dir()


def test_fail_create_run_function():
    basePath = Path("/tmp")
    runName = "testRun_21"

    try:
        RM.create_run(".", runName)
    except TypeError as e:
        assert str(e) == ("The `path_to_directory` must be a Path type object, received object of type <class 'str'>")

    try:
        RM.create_run(basePath, 2)
    except TypeError as e:
        assert str(e) == ("The `run_name` must be a str type object, received object of type <class 'int'>")

    try:
        RM.create_run(basePath, runName)
        RM.create_run(basePath, runName)
    except RuntimeError as e:
        shutil.rmtree(basePath / runName)
        assert str(e) == (
            "Unable to create the run '{}' in '{}' because a directory with that name already exists.".format(runName, str(basePath))
        )
