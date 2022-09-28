import shutil
import tempfile
from pathlib import Path

import lip_pps_run_manager as RM


class PrepareRunDir:
    def __init__(self, runName: str = "Run0001", createRunInfo: bool = True):
        self._run_name = runName
        self._create_run_info = createRunInfo
        self._tmpdir = tempfile.gettempdir()
        self._run_path = Path(self._tmpdir) / runName

    @property
    def run_path(self):
        return self._run_path

    def __enter__(self):
        self.run_path.mkdir(parents=True, exist_ok=True)

        if self._create_run_info:
            (self.run_path / "run_info.txt").touch()

        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.run_path)


def test_task_manager():
    with PrepareRunDir() as handler:
        runPath = handler.run_path
        John = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)
        assert isinstance(John, RM.TaskManager)
        assert John.task_name == "myTask"
        assert John.task_path == runPath / "myTask"
        assert not (runPath / "myTask").is_dir()


def test_fail_task_manager():
    with PrepareRunDir(createRunInfo=False) as handler:
        runPath = handler.run_path

        try:
            RM.TaskManager("runPath", "myTask", drop_old_data=True, script_to_backup=None)
        except TypeError as e:
            assert str(e) == ("The `path_to_run` must be a Path type object, received object of type <class 'str'>")

        try:
            RM.TaskManager(runPath, 2, drop_old_data=True, script_to_backup=None)
        except TypeError as e:
            assert str(e) == ("The `task_name` must be a str type object, received object of type <class 'int'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=2, script_to_backup=None)
        except TypeError as e:
            assert str(e) == ("The `drop_old_data` must be a bool type object, received object of type <class 'int'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=2)
        except TypeError as e:
            assert str(e) == ("The `script_to_backup` must be a Path type object or None, received object of type <class 'int'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)
        except RuntimeError as e:
            assert str(e) == ("The 'path_to_run' ({}) does not look like the directory of a run...".format(runPath))
