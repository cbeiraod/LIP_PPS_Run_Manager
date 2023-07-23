import copy
import datetime
import shutil
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

import humanize
import pytest
from test_run_manager_class import prepare_config_file
from test_telegram_reporter_class import SessionReplacement

import lip_pps_run_manager as RM

testdata_true_false = [(True), (False)]


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


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_no_bot():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        Tobias = RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None)

        assert isinstance(Tobias, RM.TaskManager)
        assert Tobias.task_name == task_name
        assert Tobias.task_path == handler.run_path / task_name
        assert not Tobias.task_path.is_dir()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_with_bot():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        bot_token = "bot_token"
        chat_id = "chat_id"
        Tobias = RM.TaskManager(
            handler.run_path, task_name, drop_old_data=True, script_to_backup=None, telegram_bot_token=bot_token, telegram_chat_id=chat_id
        )

        assert Tobias._bot_token == bot_token
        assert Tobias._chat_id == chat_id


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_path():
    try:
        task_name = "testTask"
        RM.TaskManager("/bad/path", task_name, drop_old_data=True, script_to_backup=None)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `path_to_run` must be a Path type object, received object of type <class 'str'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_name():
    with PrepareRunDir() as handler:
        task_name = 1

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `task_name` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_drop_old_data():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=1, script_to_backup=None)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `drop_old_data` must be a bool type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_script_to_backup():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=1)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `script_to_backup` must be a Path type object or None, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_telegram_bot_token():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None, telegram_bot_token=2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `telegram_bot_token` must be a str type object or None, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_telegram_chat_id():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None, telegram_chat_id=2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `telegram_chat_id` must be a str type object or None, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_loop_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None, loop_iterations="2")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `loop_iterations` must be a int type object or None, received object of type <class 'str'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_minimum_update_time_seconds():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None, minimum_update_time_seconds="2")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `minimum_update_time_seconds` must be a int type object, received object of type <class 'str'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_minimum_warn_time_seconds():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None, minimum_warn_time_seconds="2")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `minimum_warn_time_seconds` must be a int type object, received object of type <class 'str'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_run_directory():
    with PrepareRunDir(createRunInfo=False) as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "The 'path_to_run' ({}) does not look like the directory of a run...".format(handler.run_path)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_no_script_to_backup():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        try:
            RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=handler.run_path)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "The 'script_to_backup', if set, must point to a file. It points to: {}".format(handler.run_path)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_loop_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"

        Tobias = RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None)

        assert Tobias._loop_iterations is None
        assert Tobias._processed_iterations is None

        Luke = RM.TaskManager(handler.run_path, task_name, drop_old_data=True, script_to_backup=None, loop_iterations=20)

        assert Luke._loop_iterations == 20
        assert Luke._processed_iterations == 0
        assert Luke.processed_iterations == 0


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_repr_with_bot_ids():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        assert repr(Tobias) == (
            "TaskManager({}, {}, drop_old_data={}, "
            "script_to_backup={}, telegram_bot_token={}, "
            "telegram_chat_id={}, loop_iterations={}, "
            "minimum_update_time_seconds={}, "
            "minimum_warn_time_seconds={}, rate_limit={})".format(
                repr(handler.run_path),
                repr(task_name),
                repr(drop_old_data),
                repr(script_to_backup),
                repr(bot_token),
                repr(chat_id),
                repr(loop_iterations),
                repr(minimum_update_time_seconds),
                repr(minimum_warn_time_seconds),
                repr(rate_limit),
            )
        )


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_repr_with_bot_names():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_name = "bot_name"
        chat_name = "chat_name"
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False
        config_file = prepare_config_file(bot_name, bot_token, chat_name, chat_id)

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_name=bot_name,
            telegram_chat_name=chat_name,
            rate_limit=rate_limit,
        )

        assert repr(Tobias) == (
            "TaskManager({}, {}, drop_old_data={}, "
            "script_to_backup={}, telegram_bot_name={}, "
            "telegram_chat_name={}, loop_iterations={}, "
            "minimum_update_time_seconds={}, "
            "minimum_warn_time_seconds={}, rate_limit={})".format(
                repr(handler.run_path),
                repr(task_name),
                repr(drop_old_data),
                repr(script_to_backup),
                repr(bot_name),
                repr(chat_name),
                repr(loop_iterations),
                repr(minimum_update_time_seconds),
                repr(minimum_warn_time_seconds),
                repr(rate_limit),
            )
        )

        config_file.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_repr_no_bot():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
        )

        assert repr(Tobias) == (
            "TaskManager({}, {}, drop_old_data={}, "
            "script_to_backup={}, loop_iterations={}, "
            "minimum_update_time_seconds={}, "
            "minimum_warn_time_seconds={})".format(
                repr(handler.run_path),
                repr(task_name),
                repr(drop_old_data),
                repr(script_to_backup),
                repr(loop_iterations),
                repr(minimum_update_time_seconds),
                repr(minimum_warn_time_seconds),
            )
        )


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_expected_finish_time_no_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None

        Tobias = RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        )

        assert Tobias.expected_finish_time is None


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_expected_finish_time_with_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        Tobias = RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        )

        # Set a state where it took 60 seconds to process the first half of the iterations
        time = 60
        tolerance = 1
        Tobias._processed_iterations = int(loop_iterations / 2)
        ref_time = datetime.datetime.now()
        Tobias._start_time = ref_time - datetime.timedelta(seconds=time)
        end_time = Tobias.expected_finish_time

        assert (end_time - ref_time) > datetime.timedelta(seconds=time - tolerance)
        assert (end_time - ref_time) < datetime.timedelta(seconds=time + tolerance)

        # Set a state where it took 60 seconds to process the first 10 iterations
        time = 60
        tolerance = 1
        Tobias._processed_iterations = 10
        ref_time = datetime.datetime.now()
        Tobias._start_time = ref_time - datetime.timedelta(seconds=time)
        end_time = Tobias.expected_finish_time

        assert (end_time - ref_time) > datetime.timedelta(seconds=2 * time - tolerance)
        assert (end_time - ref_time) < datetime.timedelta(seconds=2 * time + tolerance)

        # Set a state where it took 60 seconds to process the first 20 iterations
        time = 60
        tolerance = 1
        Tobias._processed_iterations = 20
        ref_time = datetime.datetime.now()
        Tobias._start_time = ref_time - datetime.timedelta(seconds=time)
        end_time = Tobias.expected_finish_time

        assert (end_time - ref_time) > datetime.timedelta(seconds=time / 2.0 - tolerance)
        assert (end_time - ref_time) < datetime.timedelta(seconds=time / 2.0 + tolerance)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_loop_tick_outside_context():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        Tobias = RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        )

        try:
            Tobias.loop_tick()
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == ("Tried calling loop_tick() while not inside a task context. Use the 'with TaskManager as handle' syntax")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_loop_tick_sets_update():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            assert not hasattr(Tobias, '_last_update')
            Tobias.loop_tick()
            assert hasattr(Tobias, '_last_update')


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_loop_tick_sets_processed_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            assert Tobias._processed_iterations is None
            Tobias.loop_tick()
            assert Tobias._processed_iterations == 1


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_loop_tick_ticks():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            assert Tobias._processed_iterations == 0
            Tobias.loop_tick()
            assert Tobias._processed_iterations == 1
            Tobias.loop_tick()
            assert Tobias._processed_iterations == 2
            Tobias.loop_tick()
            assert Tobias._processed_iterations == 3
            Tobias.loop_tick(count=2)
            assert Tobias._processed_iterations == 5
            Tobias.loop_tick(count=2)
            assert Tobias._processed_iterations == 7


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_loop_tick_overload():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            assert Tobias._processed_iterations == 0
            Tobias.set_completed()
            assert Tobias._processed_iterations == loop_iterations
            Tobias.loop_tick()
            assert Tobias._processed_iterations == loop_iterations + 1
            assert hasattr(Tobias, "_supposedly_just_sent_warnings")
            assert (
                "The number of processed iterations has exceeded the "
                "set number of iterations.\n  - Expected 30 "
                "iterations;\n  - Processed 31 iterations" in Tobias._supposedly_just_sent_warnings
            )


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_set_completed_outside_context():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        Tobias = RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        )

        try:
            Tobias.set_completed()
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == ("Tried calling set_completed() while not inside a task context. Use the 'with TaskManager as handle' syntax")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_set_completed_no_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            assert Tobias._processed_iterations is None
            Tobias.set_completed()
            assert Tobias._processed_iterations is None


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_set_completed_with_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            assert Tobias.processed_iterations == 0
            Tobias.set_completed()
            assert Tobias.processed_iterations == loop_iterations


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_clean_task_directory():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            Tobias.create_run()

            (Tobias.task_path / "testFile.tmp").touch()
            (Tobias.task_path / "testDir").mkdir()
            assert (Tobias.task_path / "testFile.tmp").is_file()
            assert (Tobias.task_path / "testDir").is_dir()

            Tobias.clean_task_directory()
            assert not (Tobias.task_path / "testFile.tmp").is_file()
            assert not (Tobias.task_path / "testDir").is_dir()
            assert next(Tobias.task_path.iterdir(), None) is None


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_outside_context():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        Tobias = RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        )

        try:
            Tobias._update_status()
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == ("Tried calling _update_status() while not inside a task context. Use the 'with TaskManager as handle' syntax")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_no_bot():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            Tobias._update_status()  # Todo: What to test for in the no action situation?


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_edits_message():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._update_status()
            assert Tobias._telegram_reporter._session["url"] == "https://api.telegram.org/bot{}/editMessageText".format(bot_token)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_creates_status_if_not_exists():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            assert Tobias._task_status_message_id is not None
            Tobias._task_status_message_id = None
            Tobias._update_status()
            assert Tobias._task_status_message_id is not None
            assert Tobias._telegram_reporter._session["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_sets_last_update():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            assert not hasattr(Tobias, "_last_update")
            Tobias._update_status()
            assert hasattr(Tobias, "_last_update")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_sends_processing_message():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._update_status()
            assert "▶️▶️ Processing task {}".format(task_name) in Tobias._telegram_reporter._session["data"]["text"]
            assert "{} 🍀\n".format(handler.run_name) in Tobias._telegram_reporter._session["data"]["text"]
            assert "     Started" in Tobias._telegram_reporter._session["data"]["text"]
            assert "Last update of this message: " in Tobias._telegram_reporter._session["data"]["text"]


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_unknown_expected_end_no_ticks():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            assert Tobias._processed_iterations is None
            Tobias._last_update = datetime.datetime.now() - datetime.timedelta(seconds=minimum_update_time_seconds + 10)
            Tobias._update_status()
            assert "     Unknown expected finish time and remaining time\n\n" in Tobias._telegram_reporter._session["data"]["text"]
            assert "out of an unknown number of iterations\n\n\n" not in Tobias._telegram_reporter._session["data"]["text"]


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_unknown_expected_end_without_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._processed_iterations = 0
            Tobias._last_update = datetime.datetime.now() - datetime.timedelta(seconds=minimum_update_time_seconds + 10)
            Tobias._update_status()
            assert "     Unknown expected finish time and remaining time\n\n" in Tobias._telegram_reporter._session["data"]["text"]
            assert "     Progress: 0 out of an unknown number of iterations\n\n\n" in Tobias._telegram_reporter._session["data"]["text"]

            Tobias.loop_tick()
            Tobias._last_update = datetime.datetime.now() - datetime.timedelta(seconds=minimum_update_time_seconds + 10)
            Tobias._update_status()
            assert "     Unknown expected finish time and remaining time\n\n" in Tobias._telegram_reporter._session["data"]["text"]
            assert "     Progress: 1 out of an unknown number of iterations\n\n\n" in Tobias._telegram_reporter._session["data"]["text"]


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_unknown_expected_end_with_iterations():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._processed_iterations = 0
            Tobias._last_update = datetime.datetime.now() - datetime.timedelta(seconds=minimum_update_time_seconds + 10)
            Tobias._update_status()
            assert "     Unknown expected finish time and remaining time\n\n" in Tobias._telegram_reporter._session["data"]["text"]
            assert (
                "     Progress: 0 out of {} iterations\n\n\n".format(loop_iterations) in Tobias._telegram_reporter._session["data"]["text"]
            )


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_update_status_expected_end():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias.loop_tick()
            Tobias._last_update = datetime.datetime.now() - datetime.timedelta(seconds=minimum_update_time_seconds + 10)
            Tobias._update_status()
            assert "     Expected finish: " in Tobias._telegram_reporter._session["data"]["text"]
            assert "     Remaining time: " in Tobias._telegram_reporter._session["data"]["text"]
            assert (
                "     Progress: {} % ({}/{})\n\n\n".format(
                    int(Tobias.processed_iterations / loop_iterations * 100), int(Tobias.processed_iterations), int(loop_iterations)
                )
                in Tobias._telegram_reporter._session["data"]["text"]
            )

            Tobias.loop_tick()
            Tobias.loop_tick()
            Tobias.loop_tick()
            Tobias._last_update = datetime.datetime.now() - datetime.timedelta(seconds=minimum_update_time_seconds + 10)
            Tobias._update_status()
            assert "     Expected finish: " in Tobias._telegram_reporter._session["data"]["text"]
            assert "     Remaining time: " in Tobias._telegram_reporter._session["data"]["text"]
            assert (
                "     Progress: {} % ({}/{})\n\n\n".format(
                    int(Tobias.processed_iterations / loop_iterations * 100), int(Tobias.processed_iterations), int(loop_iterations)
                )
                in Tobias._telegram_reporter._session["data"]["text"]
            )


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_double_entry():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        with Tobias:
            pass

        try:
            with Tobias:
                pass  # pragma: no cover
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "Once a task has processed its data, it can not be processed again. Use a new task"


@pytest.mark.parametrize("drop_old_data", testdata_true_false)
@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_cleans_directory(drop_old_data: bool):
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        Tobias.task_path.mkdir()
        (Tobias.task_path / "testFile.tmp").touch()
        (Tobias.task_path / "testDir").mkdir()
        assert (Tobias.task_path / "testFile.tmp").is_file()
        assert (Tobias.task_path / "testDir").is_dir()

        with Tobias as tobias:
            assert (tobias.task_path / "testFile.tmp").is_file() != drop_old_data
            assert (tobias.task_path / "testDir").is_dir() != drop_old_data


@pytest.mark.parametrize("own_run_context", testdata_true_false)
@pytest.mark.parametrize("create_bot", testdata_true_false)
@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_creates_run_context(own_run_context: bool, create_bot: bool):
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        if create_bot:
            bot_token = "bot_token"
            chat_id = "chat_id"
            rate_limit = False
        else:
            bot_token = None
            chat_id = None
            rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )
        if not own_run_context:
            Tobias._in_run_context = True

        with Tobias as tobias:
            assert tobias._own_run_context == own_run_context
            if own_run_context and create_bot:
                assert isinstance(tobias._telegram_reporter, RM.TelegramReporter)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_creates_task_context():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        with Tobias as tobias:
            assert tobias._in_task_context


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_creates_start_time():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        assert not hasattr(Tobias, "_start_time")

        with Tobias as tobias:
            assert isinstance(tobias._start_time, datetime.datetime)


@pytest.mark.parametrize("with_loop_iterations", testdata_true_false)
@pytest.mark.parametrize("create_bot", testdata_true_false)
@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_creates_status_message(with_loop_iterations: bool, create_bot: bool):
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        if with_loop_iterations:
            loop_iterations = 30
        else:
            loop_iterations = None
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        if create_bot:
            bot_token = "bot_token"
            chat_id = "chat_id"
            rate_limit = False
        else:
            bot_token = None
            chat_id = None
            rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        assert Tobias._task_status_message_id is None

        with Tobias as tobias:
            if create_bot:  # TODO: What if there is no bot... what should we test?
                assert tobias._task_status_message_id is not None
                assert "Started processing task" in tobias._telegram_reporter._session["data"]["text"]
                if with_loop_iterations:
                    assert ".\nIt has " in tobias._telegram_reporter._session["data"]["text"]
                else:
                    assert ".\nIt has " not in tobias._telegram_reporter._session["data"]["text"]
                assert "\nAn update should come soon" in tobias._telegram_reporter._session["data"]["text"]


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_sets_processed_flag():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )
        assert not hasattr(Tobias, "_already_processed")

        with Tobias as tobias:
            assert not hasattr(tobias, "_already_processed")
        assert Tobias._already_processed


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_ends_task_context():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )
        assert not Tobias._in_task_context

        with Tobias as tobias:
            assert tobias._in_task_context
        assert not Tobias._in_task_context


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_creates_task_report():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        with Tobias as tobias:
            assert not (tobias.task_path / "task_report.txt").is_file()
        assert (Tobias.task_path / "task_report.txt").is_file()


testdata_task_end_types = [("no errors"), ("incomplete"), ("errors")]


@pytest.mark.parametrize("task_end_type", testdata_task_end_types)
@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_task_report_content(task_end_type: str):
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = None
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        try:
            with Tobias as tobias:
                if task_end_type == "errors":
                    raise Exception("Just to get out")
                elif task_end_type == "incomplete":
                    tobias.loop_tick()
                    tobias.loop_tick()
                    tobias.loop_tick()
                else:  # elif task_end_type == "no errors"
                    tobias.set_completed()
        except Exception:
            pass

        with open(Tobias.task_path / "task_report.txt", "r", encoding="utf8") as report_file:
            first_line = report_file.readline()
            if task_end_type == "errors":
                assert first_line == "task_status: there were errors\n"  # Test that the content of the report file is correct
            elif task_end_type == "incomplete":
                assert first_line == "task_status: incomplete\n"  # Test that the content of the report file is correct
            else:  # elif task_end_type == "no errors"
                assert first_line == "task_status: no errors\n"  # Test that the content of the report file is correct


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_backup_file_does_not_exist():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        try:
            with RM.TaskManager(
                handler.run_path,
                task_name,
                drop_old_data=drop_old_data,
                script_to_backup=script_to_backup,
                loop_iterations=loop_iterations,
                minimum_update_time_seconds=minimum_update_time_seconds,
                minimum_warn_time_seconds=minimum_warn_time_seconds,
                telegram_bot_token=bot_token,
                telegram_chat_id=chat_id,
                rate_limit=rate_limit,
            ) as Tobias:
                Tobias._script_to_backup = handler.run_path
                raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "Somehow you are trying to backup a file that does not exist"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_backup_file_created():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        with Tobias:
            pass

        assert (Tobias.task_path / "backup.{}".format(Path(traceback.extract_stack()[-1].filename).parts[-1])).is_file()


@pytest.mark.parametrize("own_run_context", testdata_true_false)
@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_sets_run_context(own_run_context: bool):
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )
        if not own_run_context:
            Tobias._in_run_context = True

        with Tobias as tobias:
            assert tobias._own_run_context == own_run_context

            assert tobias._in_run_context

        assert tobias._in_run_context != own_run_context


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_warn_bad_type_message():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        try:
            Tobias.warn(2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `message` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_warn_creates_accumulated_warnings():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        assert not hasattr(Tobias, "_accumulated_warnings")

        Tobias.warn("Test warn")

        assert hasattr(Tobias, "_accumulated_warnings")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_warn_already_has_accumulated_warnings():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        assert not hasattr(Tobias, "_accumulated_warnings")
        Tobias._accumulated_warnings = {}
        assert hasattr(Tobias, "_accumulated_warnings")

        Tobias.warn("Test warn")

        assert hasattr(Tobias, "_accumulated_warnings")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_warn_accumulates_warnings():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        test_warning1 = "Test warn"

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._last_warn = datetime.datetime.now()

            Tobias.warn(test_warning1)
            assert hasattr(Tobias, "_accumulated_warnings")
            assert test_warning1 in Tobias._accumulated_warnings
            assert Tobias._accumulated_warnings[test_warning1] == 1

            Tobias.warn(test_warning1)
            assert Tobias._accumulated_warnings[test_warning1] == 2


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_returns_no_accumulated_warnings():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        assert not hasattr(Tobias, "_accumulated_warnings")

        Tobias._send_warnings()  # TODO: is there a better way to test a return with no change of state?

        assert not hasattr(Tobias, "_accumulated_warnings")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_no_bot_creates_warn_backup():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = None
        chat_id = None
        rate_limit = False

        accumulated_warnings = {"This is message 1": 1, "This message was repeated": 2}

        Tobias = RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        )

        Tobias._accumulated_warnings = copy.deepcopy(accumulated_warnings)

        Tobias._send_warnings()

        assert Tobias._supposedly_just_sent_warnings == accumulated_warnings


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_without_task_status_message_id():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        accumulated_warnings = {"This is message 1": 1, "This message was repeated": 2}

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._accumulated_warnings = copy.deepcopy(accumulated_warnings)
            Tobias._telegram_reporter._session._clear()
            Tobias._task_status_message_id = None
            Tobias._last_warn = datetime.datetime.now() - datetime.timedelta(seconds=minimum_warn_time_seconds + 10)
            Tobias._send_warnings()

            assert Tobias._telegram_reporter._session._params == {}  # Test that no message was sent
            # TODO: is there a better way to test no effect?


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_sets_last_warn():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        accumulated_warnings = {"This is message 1": 1, "This message was repeated": 2}

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            assert not hasattr(Tobias, "_last_warn")
            Tobias._accumulated_warnings = copy.deepcopy(accumulated_warnings)

            Tobias._send_warnings()

            assert Tobias._last_warn is not None


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_not_enough_time():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        accumulated_warnings = {"This is message 1": 1, "This message was repeated": 2}

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._last_warn = datetime.datetime.now()
            Tobias._accumulated_warnings = copy.deepcopy(accumulated_warnings)

            Tobias._send_warnings()

            assert Tobias._accumulated_warnings == accumulated_warnings


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_single_warning():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        message1 = "This is message 1"
        # message2 = "This message was repeated"
        accumulated_warnings = {
            message1: 1,
            # message2: 2
        }

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._last_warn = datetime.datetime.now() - datetime.timedelta(seconds=minimum_warn_time_seconds + 10)
            Tobias._accumulated_warnings = copy.deepcopy(accumulated_warnings)

            Tobias._send_warnings()

            assert Tobias._telegram_reporter._session["data"]["text"] == message1
            assert Tobias._accumulated_warnings == {}


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_single_warning_repeated():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        message1 = "This is message 1"
        repeats = 2
        # message2 = "This message was repeated"
        accumulated_warnings = {
            message1: repeats,
            # message2: 2
        }

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._last_warn = datetime.datetime.now() - datetime.timedelta(seconds=minimum_warn_time_seconds + 10)
            Tobias._accumulated_warnings = copy.deepcopy(accumulated_warnings)

            Tobias._send_warnings()

            assert message1 in Tobias._telegram_reporter._session["data"]["text"]
            assert (
                "Received the following warning {} times in the last {}:\n".format(
                    repeats, humanize.naturaldelta(minimum_warn_time_seconds)
                )
                in Tobias._telegram_reporter._session["data"]["text"]
            )
            assert Tobias._accumulated_warnings == {}


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_warnings_multiple_warnings():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        script_to_backup = Path(traceback.extract_stack()[-1].filename)
        drop_old_data = True
        loop_iterations = 30
        minimum_update_time_seconds = 60
        minimum_warn_time_seconds = 60
        bot_token = "bot_token"
        chat_id = "chat_id"
        rate_limit = False

        message1 = "This is message 1"
        repeats = 2
        message2 = "This message was repeated"
        accumulated_warnings = {message1: 1, message2: repeats}

        with RM.TaskManager(
            handler.run_path,
            task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
            telegram_bot_token=bot_token,
            telegram_chat_id=chat_id,
            rate_limit=rate_limit,
        ) as Tobias:
            Tobias._last_warn = datetime.datetime.now() - datetime.timedelta(seconds=minimum_warn_time_seconds + 10)
            Tobias._accumulated_warnings = copy.deepcopy(accumulated_warnings)

            Tobias._send_warnings()

            assert (
                "Several warnings received in the last {}\n".format(humanize.naturaldelta(minimum_warn_time_seconds))
                in Tobias._telegram_reporter._session["data"]["text"]
            )
            assert "Received the following warning {} times:\n".format(1) not in Tobias._telegram_reporter._session["data"]["text"]
            assert "Received the following warning {} times:\n".format(repeats) in Tobias._telegram_reporter._session["data"]["text"]
            assert message1 in Tobias._telegram_reporter._session["data"]["text"]
            assert message2 in Tobias._telegram_reporter._session["data"]["text"]
            assert Tobias._accumulated_warnings == {}


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None

        source = handler.run_path / "test_in_file.txt"

        assert not source.exists()

        with open(source, "w") as file:
            file.write("Hello!\n")
            file.write("This is a test file\n")

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            Tobias.backup_file(source)

            assert (Tobias.task_path / (source.name + ".bak")).exists()

            import filecmp

            assert filecmp.cmp(source, (Tobias.task_path / (source.name + ".bak")))

        source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file_bad_type_source():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None

        source = 2

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            try:
                Tobias.backup_file(source)
                raise Exception("Passed through a fail condition without failing")  # pragma: no cover
            except TypeError as e:
                assert str(e) == "The `source` must be a Path type object, received object of type <class 'int'> instead"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file_source_does_not_exist():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None

        source = handler.run_path / "test_in_file.txt"

        assert not source.exists()

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            try:
                Tobias.backup_file(source)
                raise Exception("Passed through a fail condition without failing")  # pragma: no cover
            except RuntimeError as e:
                assert str(e) == "The source file does not exist or it is not a file."


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file_source_is_not_file():
    with PrepareRunDir() as handler:
        task_name = "testTask"
        drop_old_data = True
        script_to_backup = None
        loop_iterations = None

        source = handler.run_path

        with RM.TaskManager(
            handler.run_path, task_name, drop_old_data=drop_old_data, script_to_backup=script_to_backup, loop_iterations=loop_iterations
        ) as Tobias:
            try:
                Tobias.backup_file(source)
                raise Exception("Passed through a fail condition without failing")  # pragma: no cover
            except RuntimeError as e:
                assert str(e) == "The source file does not exist or it is not a file."
