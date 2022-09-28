import shutil
from pathlib import Path

import lip_pps_run_manager as RM
import lip_pps_run_manager.run_manager as internalRM


def test_run_manager():
    John = RM.RunManager(Path("/tmp/Run0001"))
    assert John.path_directory == Path("/tmp/Run0001")
    assert John.run_name == "Run0001"


def test_fail_run_manager():
    try:
        RM.RunManager(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_run_directory` must be a Path type object, received object of type <class 'str'>")


def test_run_manager_create_run():
    runPath = Path("/tmp/Run0001")
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)
    assert runPath.is_dir()
    try:
        John.create_run(raise_error=True)
    except RuntimeError as e:
        assert str(e) == ("Can not create run '{}', in '{}' because it already exists.".format("Run0001", "/tmp"))
    John.create_run(raise_error=False)
    (runPath / "run_info.txt").unlink()
    try:
        John.create_run(raise_error=False)
    except RuntimeError as e:
        assert str(e) == (
            "Unable to create the run '{}' in '{}' because a directory with that name already exists.".format("Run0001", "/tmp")
        )
    shutil.rmtree(runPath)


def test_run_manager_handle_task():
    runPath = Path("/tmp/Run0001")
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)

    TaskHandler = John.handle_task("myTask")
    assert isinstance(TaskHandler, RM.TaskManager)
    shutil.rmtree(runPath)


def test_fail_run_manager_handle_task():
    runPath = Path("/tmp/Run0001")
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)

    try:
        John.handle_task(1)
    except TypeError as e:
        assert str(e) == ("The `task_name` must be a str type object, received object of type <class 'int'>")

    try:
        John.handle_task("myTask", drop_old_data=1)
    except TypeError as e:
        assert str(e) == ("The `drop_old_data` must be a bool type object, received object of type <class 'int'>")

    try:
        John.handle_task("myTask", backup_python_file=1)
    except TypeError as e:
        assert str(e) == ("The `backup_python_file` must be a bool type object, received object of type <class 'int'>")

    shutil.rmtree(runPath)


def test_run_exists_function():
    runName = "hopefully_unique_run_name"
    p = Path("/tmp") / runName
    p.mkdir(exist_ok=True)
    (p / 'run_info.txt').touch()
    assert internalRM.run_exists(Path("/tmp"), runName)  # Test when exists
    shutil.rmtree(p)
    assert not internalRM.run_exists(Path("/tmp"), runName)  # Test when doesn't exist


def test_fail_run_exists_function():
    try:
        internalRM.run_exists(".", "a")
    except TypeError as e:
        assert str(e) == ("The `path_to_directory` must be a Path type object, received object of type <class 'str'>")

    try:
        internalRM.run_exists(Path("."), 2)
    except TypeError as e:
        assert str(e) == ("The `run_name` must be a str type object, received object of type <class 'int'>")


def test_clean_path_function():
    assert isinstance(internalRM.clean_path(Path(".")), Path)  # Test return type
    # TODO: assert RM.clean_path(Path("./Run@2")) == Path("./Run2") # Test actual cleaning


def test_fail_clean_path_function():
    try:
        internalRM.clean_path(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_clean` must be a Path type object, received object of type <class 'str'>")


def test_create_run_function():
    basePath = Path("/tmp")
    runName = "testRun_21"

    assert internalRM.create_run(basePath, runName) == basePath / runName
    assert (basePath / runName).is_dir()
    assert (basePath / runName / "run_info.txt").is_file()
    # TODO: Check contents of run_info.txt file
    shutil.rmtree(basePath / runName)
    assert not (basePath / runName).is_dir()


def test_fail_create_run_function():
    basePath = Path("/tmp")
    runName = "testRun_21"

    try:
        internalRM.create_run(".", runName)
    except TypeError as e:
        assert str(e) == ("The `path_to_directory` must be a Path type object, received object of type <class 'str'>")

    try:
        internalRM.create_run(basePath, 2)
    except TypeError as e:
        assert str(e) == ("The `run_name` must be a str type object, received object of type <class 'int'>")

    try:
        internalRM.create_run(basePath, runName)
        internalRM.create_run(basePath, runName)
    except RuntimeError as e:
        shutil.rmtree(basePath / runName)
        assert str(e) == (
            "Unable to create the run '{}' in '{}' because a directory with that name already exists.".format(runName, str(basePath))
        )
