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
        self.run_path.mkdir(parents=True)

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
        assert John.task_directory == runPath / "myTask"
        assert not (runPath / "myTask").is_dir()
