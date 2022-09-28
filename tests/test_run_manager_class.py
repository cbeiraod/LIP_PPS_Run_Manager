import shutil
import tempfile
import traceback
from pathlib import Path

import lip_pps_run_manager as RM


def ensure_clean(path: Path):  # pragma: no cover
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def test_run_manager():
    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    John = RM.RunManager(runPath)
    assert John.path_directory == runPath
    assert John.run_name == "Run0001"


def test_fail_run_manager():
    try:
        RM.RunManager(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_run_directory` must be a Path type object, received object of type <class 'str'>")


def test_run_manager_create_run():
    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)
    assert runPath.is_dir()
    try:
        John.create_run(raise_error=True)
    except RuntimeError as e:
        assert str(e) == ("Can not create run '{}', in '{}' because it already exists.".format("Run0001", tmpdir))
    John.create_run(raise_error=False)
    (runPath / "run_info.txt").unlink()
    try:
        John.create_run(raise_error=False)
    except RuntimeError as e:
        assert str(e) == (
            "Unable to create the run '{}' in '{}' because a directory with that name already exists.".format("Run0001", tmpdir)
        )
    shutil.rmtree(runPath)


def test_run_manager_get_task_path():
    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)

    path = John.get_task_path("myTask")

    assert isinstance(path, Path)
    assert not path.is_dir()

    shutil.rmtree(runPath)


def test_fail_run_manager_get_task_path():
    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)

    try:
        John.get_task_path(2)
    except TypeError as e:
        assert str(e) == ("The `task_name` must be a str type object, received object of type <class 'int'>")

    shutil.rmtree(runPath)


def test_run_manager_handle_task():
    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)

    TaskHandler = John.handle_task("myTask")
    assert isinstance(TaskHandler, RM.TaskManager)
    assert TaskHandler.task_name == "myTask"
    assert TaskHandler.task_path == runPath / "myTask"
    assert TaskHandler._script_to_backup == Path(traceback.extract_stack()[-1].filename)

    TaskHandler2 = John.handle_task("myTask2", backup_python_file=False)
    assert isinstance(TaskHandler2, RM.TaskManager)
    assert TaskHandler2.task_name == "myTask2"
    assert TaskHandler2.task_path == runPath / "myTask2"
    assert TaskHandler2._script_to_backup is None
    shutil.rmtree(runPath)


def test_fail_run_manager_handle_task():
    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
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
