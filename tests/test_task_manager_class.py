import copy
import shutil
import tempfile
import time
import traceback
from pathlib import Path

import humanize

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
            john.loop_tick()
            assert John.processed_iterations == 21
            assert hasattr(john, "_supposedly_just_sent_warnings")
            assert (
                "The number of processed iterations has exceeded the "
                "set number of iterations.\n  - Expected 20 "
                "iterations;\n  - Processed 21 iterations" in john._supposedly_just_sent_warnings
            )


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


def test_task_manager_warn():
    with PrepareRunDir() as handler:
        runPath = handler.run_path
        John = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)

        warn_message = "Hello! This is a warning"

        assert not hasattr(John, "_accumulated_warnings")
        John.warn(warn_message)
        assert hasattr(John, "_accumulated_warnings")
        assert John._accumulated_warnings == {}
        assert hasattr(John, "_supposedly_just_sent_warnings")
        assert warn_message in John._supposedly_just_sent_warnings
        assert John._supposedly_just_sent_warnings[warn_message] == 1

    with PrepareRunDir() as handler:
        from test_telegram_reporter_class import SessionReplacement

        sessionHandler = SessionReplacement()

        bot_token = "bot_token"
        chat_id = "chat_id"
        warn_time = 3600  # 1 hour wait, like this we can test that the messages are correctly accumulated

        runPath = handler.run_path
        John = RM.TaskManager(
            runPath,
            "myTask",
            drop_old_data=True,
            script_to_backup=None,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            minimum_warn_time_seconds=warn_time,
        )
        John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests

        warn_message = "Hello! This is a warning"

        assert not hasattr(John, "_accumulated_warnings")
        John.warn(warn_message)
        assert hasattr(John, "_accumulated_warnings")
        assert warn_message in John._accumulated_warnings
        assert John._accumulated_warnings[warn_message] == 1

        with John as john:
            assert not hasattr(john, "_last_warn")
            john.warn(warn_message)
            assert hasattr(john, "_last_warn")
            assert john._accumulated_warnings == {}
            httpRequest = sessionHandler.json()
            assert httpRequest["timeout"] == 1
            assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
            assert httpRequest["data"]['chat_id'] == chat_id
            sent_message = "Received the following warning {} times in the last {}:\n".format(2, humanize.naturaldelta(3600)) + warn_message
            assert httpRequest["data"]['text'] == sent_message

            try:
                john.warn(2)
            except TypeError as e:
                assert str(e) == "The `message` must be a str type object, received object of type <class 'int'>"


def test_task_manager_send_warnings():
    with PrepareRunDir() as handler:
        runPath = handler.run_path
        John = RM.TaskManager(runPath, "myTask", drop_old_data=True, script_to_backup=None)

        John._send_warnings()
        assert not hasattr(John, "_accumulated_warnings")

        tmpVar = {}
        John._accumulated_warnings = copy.deepcopy(tmpVar)
        John._send_warnings()
        assert not hasattr(John, "_supposedly_just_sent_warnings")
        assert John._accumulated_warnings == tmpVar

        tmpVar = {"message1": 1, "message2": 2}
        John._accumulated_warnings = copy.deepcopy(tmpVar)
        John._send_warnings()
        assert hasattr(John, "_supposedly_just_sent_warnings")
        assert John._supposedly_just_sent_warnings == tmpVar

    with PrepareRunDir() as handler:
        from test_telegram_reporter_class import SessionReplacement

        sessionHandler = SessionReplacement()

        bot_token = "bot_token"
        chat_id = "chat_id"
        warn_time = 1

        runPath = handler.run_path
        John = RM.TaskManager(
            runPath,
            "myTask",
            drop_old_data=True,
            script_to_backup=None,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            minimum_warn_time_seconds=warn_time,
        )
        John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests

        assert not hasattr(John, "_last_warn")

        tmpVar = {"test": 2}
        John._accumulated_warnings = copy.deepcopy(tmpVar)
        assert John._telegram_reporter is not None
        assert John._task_status_message_id is None
        John._send_warnings()
        assert not hasattr(John, "_last_warn")

        message1 = "message1"
        message2 = "message2"
        times = 10

        with John as john:
            assert John._telegram_reporter is not None
            assert John._task_status_message_id is not None

            # Test Single warning message, sent a single time
            tmpVar = {message1: 1}
            john._accumulated_warnings = copy.deepcopy(tmpVar)
            john._send_warnings()
            assert hasattr(john, "_last_warn")
            assert not hasattr(john, "_supposedly_just_sent_warnings")
            assert john._accumulated_warnings == {}
            httpRequest = sessionHandler.json()
            assert httpRequest["timeout"] == 1
            assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
            assert httpRequest["data"]['chat_id'] == chat_id
            assert httpRequest["data"]['text'] == message1

            tmpVar = {message1: times}
            john._accumulated_warnings = copy.deepcopy(tmpVar)
            john._send_warnings()
            assert john._accumulated_warnings == tmpVar

            time.sleep(warn_time + 0.1)

            # Test Single warning message, sent more than one time
            tmpVar = {message1: times}
            john._accumulated_warnings = copy.deepcopy(tmpVar)
            john._send_warnings()
            assert not hasattr(john, "_supposedly_just_sent_warnings")
            assert john._accumulated_warnings == {}
            httpRequest = sessionHandler.json()
            assert httpRequest["timeout"] == 1
            assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
            assert httpRequest["data"]['chat_id'] == chat_id
            assert (
                httpRequest["data"]['text']
                == "Received the following warning {} times in the last {}:\n".format(times, humanize.naturaldelta(warn_time)) + message1
            )

            time.sleep(warn_time + 0.1)

            # Test multiple warning messages
            tmpVar = {message1: times, message2: 1}
            john._accumulated_warnings = copy.deepcopy(tmpVar)
            john._send_warnings()
            assert not hasattr(john, "_supposedly_just_sent_warnings")
            assert john._accumulated_warnings == {}
            httpRequest = sessionHandler.json()
            assert httpRequest["timeout"] == 1
            assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
            assert httpRequest["data"]['chat_id'] == chat_id
            message_sent = "Several warnings received in the last {}\n".format(humanize.naturaldelta(warn_time))
            for msg, count in tmpVar.items():
                message_sent += "\n----------------------------------\n"
                if count > 1:
                    message_sent += "Received the following warning {} times:\n".format(count)
                message_sent += msg
            assert httpRequest["data"]['text'] == message_sent


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
