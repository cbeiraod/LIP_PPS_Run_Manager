import shutil
import tempfile
import traceback
from pathlib import Path

import lip_pps_run_manager as RM


class PrepareRunDir:
    def __init__(self, runName: str = "Run0001", createRunInfo: bool = True):
        self._run_name = runName
        self._create_run_info = createRunInfo
        self._tmpdir = tempfile.gettempdir()
        self._run_path = Path(self._tmpdir) / runName

    @property
    def run_path(self):  # pragma: no cover
        return self._run_path

    @property
    def run_name(self):  # pragma: no cover
        return self._run_name

    @property
    def run_dir(self):  # pragma: no cover
        return self._tmpdir

    def __enter__(self):
        if self.run_path.exists():  # pragma: no cover
            shutil.rmtree(self.run_path)

        self.run_path.mkdir(parents=True)

        if self._create_run_info:
            (self.run_path / "run_info.txt").touch()

        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.run_path)


def test_task_manager():
    with PrepareRunDir() as handler:
        runPath = handler.run_path
        John = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None, loop_iterations=20)
        assert isinstance(John, RM.TaskManager)
        assert John.task_name == "myTask"
        assert John.task_path == runPath / "myTask"
        assert not (runPath / "myTask").is_dir()
        assert John.processed_iterations == 0

        try:
            John.loop_tick()
        except RuntimeError as e:
            assert str(e) == ("Tried calling loop_tick() while not inside a task context. Use the 'with TaskManager as handle' syntax")

        try:
            John.set_completed()
        except RuntimeError as e:
            assert str(e) == ("Tried calling set_completed() while not inside a task context. Use the 'with TaskManager as handle' syntax")

        with John as john:
            john.loop_tick()
            assert John.processed_iterations == 1
            john.set_completed()
            assert John.processed_iterations == 20


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
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None, telegram_bot_token=20)
        except TypeError as e:
            assert str(e) == ("The `telegram_bot_token` must be a str type object or None, received object of type <class 'int'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None, telegram_chat_id=20)
        except TypeError as e:
            assert str(e) == ("The `telegram_chat_id` must be a str type object or None, received object of type <class 'int'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None, loop_iterations="20")
        except TypeError as e:
            assert str(e) == ("The `loop_iterations` must be a int type object or None, received object of type <class 'str'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=2)
        except TypeError as e:
            assert str(e) == ("The `script_to_backup` must be a Path type object or None, received object of type <class 'int'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, loop_iterations="2")
        except TypeError as e:
            assert str(e) == ("The `loop_iterations` must be a int type object or None, received object of type <class 'str'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, minimum_update_time_seconds="2")
        except TypeError as e:
            assert str(e) == ("The `minimum_update_time_seconds` must be a int type object, received object of type <class 'str'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, minimum_warn_time_seconds="2")
        except TypeError as e:
            assert str(e) == ("The `minimum_warn_time_seconds` must be a int type object, received object of type <class 'str'>")

        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)
        except RuntimeError as e:
            assert str(e) == ("The 'path_to_run' ({}) does not look like the directory of a run...".format(runPath))

    with PrepareRunDir() as handler:
        runPath = handler.run_path
        try:
            RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=runPath)
        except RuntimeError as e:
            assert str(e) == ("The 'script_to_backup', if set, must point to a file. It points to: {}".format(runPath))


def test_task_manager_clean_task_directory():
    with PrepareRunDir() as handler:
        runPath = handler.run_path
        John = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)
        John.create_run()
        John.task_path.mkdir()

        (John.task_path / "testFile.tmp").touch()
        (John.task_path / "testDir").mkdir()
        assert (John.task_path / "testFile.tmp").is_file()
        assert (John.task_path / "testDir").is_dir()

        John.clean_task_directory()
        assert not (John.task_path / "testFile.tmp").is_file()
        assert not (John.task_path / "testDir").is_dir()
        assert next(John.task_path.iterdir(), None) is None


def test_task_manager_with():
    with PrepareRunDir() as handler:
        runPath = handler.run_path
        John = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)
        John.create_run()

        with John as john:
            (john.task_path / "task_file.txt").touch()
        assert (John.task_path / "task_report.txt").is_file()  # Test the __exit__ is correctly creating the report file

        with open(John.task_path / "task_report.txt") as report_file:
            first_line = report_file.readline()
            assert first_line == "task_status: no errors\n"  # Test that the content of the report file is correct

        try:
            with John as john:  # Test __enter__ not allowing to reuse a TaskManager
                pass  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == ("Once a task has processed its data, it can not be processed again. Use a new task")

        John2 = RM.TaskManager(runPath, "myTask", drop_old_data=False, script_to_backup=None)
        John2.create_run()
        with John2 as john:
            assert (john.task_path / "task_file.txt").is_file()  # Test __enter__ does not delete old files if not asked to

        try:
            John3 = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=Path(traceback.extract_stack()[-1].filename))
            John3.create_run()
            with John3 as john:
                assert not (john.task_path / "task_file.txt").is_file()  # Test __enter__ does delete old files when asked to
                raise RuntimeError(
                    "This is to test the TaskManager error handling"
                )  # Create an artificial error to trigger the report file to have error content in it
        except RuntimeError as e:
            assert str(e) == "This is to test the TaskManager error handling"
        with open(John3.task_path / "task_report.txt") as report_file:
            first_line = report_file.readline()
            assert first_line == "task_status: there were errors\n"  # Test that the content of the report file is correct

        assert (
            John3.task_path / "backup.{}".format(Path(traceback.extract_stack()[-1].filename).parts[-1])
        ).is_file()  # Test script backing up

        try:
            John4 = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=Path(traceback.extract_stack()[-1].filename))
            John4.create_run()
            with John4 as john:
                John4._script_to_backup = runPath
        except RuntimeError as e:
            assert str(e) == "Somehow you are trying to backup a file that does not exist"


def test_task_manager_repr():
    from test_telegram_reporter_class import SessionReplacement

    sessionHandler = SessionReplacement()

    with PrepareRunDir() as handler:
        runPath = handler.run_path
        bot_token = "bot_token"
        chat_id = "chat_id"

        John = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)
        assert repr(John) == "TaskManager({}, {}, drop_old_data={}, script_to_backup={})".format(
            repr(runPath), repr("myTask"), repr(True), repr(None)
        )

        John = RM.TaskManager(
            runPath, "myTask", drop_old_data=True, script_to_backup=None, telegram_bot_token=bot_token, telegram_chat_id=chat_id
        )
        John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests
        assert repr(
            John
        ) == "TaskManager({}, {}, drop_old_data={}, script_to_backup={}, telegram_bot_token={}, telegram_chat_id={})".format(
            repr(runPath), repr("myTask"), repr(True), repr(None), repr(bot_token), repr(chat_id)
        )
