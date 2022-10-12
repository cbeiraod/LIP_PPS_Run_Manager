import shutil
import tempfile
import traceback
from pathlib import Path

import lip_pps_run_manager as RM


def ensure_clean(path: Path):  # pragma: no cover
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def test_run_manager():
    from test_telegram_reporter_class import SessionReplacement

    sessionHandler = SessionReplacement()

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    John = RM.RunManager(runPath)
    assert John.path_directory == runPath
    assert John.run_name == "Run0001"

    John = RM.RunManager(runPath, telegram_bot_token="bot_token", telegram_chat_id="chat_id")
    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests
    assert isinstance(John._telegram_reporter, RM.TelegramReporter)


def test_fail_run_manager():
    try:
        RM.RunManager(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_run_directory` must be a Path type object, received object of type <class 'str'>")

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)

    try:
        RM.RunManager(runPath, telegram_bot_token=2)
    except TypeError as e:
        assert str(e) == ("The `telegram_bot_token` must be a str type object, received object of type <class 'int'>")
    try:
        RM.RunManager(runPath, telegram_chat_id=2)
    except TypeError as e:
        assert str(e) == ("The `telegram_chat_id` must be a str type object, received object of type <class 'int'>")


def test_run_manager_create_run():
    from test_telegram_reporter_class import SessionReplacement

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    sessionHandler = SessionReplacement()
    ensure_clean(runPath)
    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id)
    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests

    John.create_run(raise_error=True)

    assert runPath.is_dir()
    httpRequest = sessionHandler.json()
    assert httpRequest["timeout"] == 1
    assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    assert httpRequest["data"]['chat_id'] == chat_id
    # assert httpRequest["data"]['text'] == message  # Not testing the message contents so that we are free to change as needed
    assert John._status_message_id == "This is the message ID"

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

    sessionHandler.clear()

    # del John
    John = None
    httpRequest = sessionHandler.json()
    assert httpRequest["timeout"] == 1
    assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    assert httpRequest["data"]['chat_id'] == chat_id
    assert httpRequest["data"]['text'] == "✔️ Finished processing Run Run0001"

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
    from test_telegram_reporter_class import SessionReplacement

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    ensure_clean(runPath)
    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id)
    John._telegram_reporter._session = SessionReplacement()  # To avoid sending actual http requests
    # John.create_run(raise_error=True)

    TaskHandler = John.handle_task("myTask", telegram_loop_iterations=20)
    assert isinstance(TaskHandler, RM.TaskManager)
    assert TaskHandler.task_name == "myTask"
    assert TaskHandler.task_path == runPath / "myTask"
    assert TaskHandler._script_to_backup == Path(traceback.extract_stack()[-1].filename)
    assert isinstance(TaskHandler._telegram_reporter, RM.TelegramReporter)

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

    try:
        John.handle_task("myTask", telegram_loop_iterations="2")
    except TypeError as e:
        assert str(e) == ("The `telegram_loop_iterations` must be a int type object or None, received object of type <class 'str'>")

    shutil.rmtree(runPath)


def test_run_manager_send_message():
    from test_telegram_reporter_class import SessionReplacement

    sessionHandler = SessionReplacement()

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    bot_token = "bot_token"
    chat_id = "chat_id"
    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id)
    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests

    message_id = John.send_message("This is a test message")

    assert message_id == "This is the message ID"
    httpRequest = sessionHandler.json()
    assert httpRequest["timeout"] == 1
    assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    assert httpRequest["data"]['chat_id'] == chat_id
    # assert httpRequest["data"]['text'] == ""  # Not testing message content

    reply_message_id = "reply_to_me"
    message_id = John.send_message("This is a test message", reply_message_id)

    assert message_id == "This is the message ID"
    httpRequest = sessionHandler.json()
    assert httpRequest["timeout"] == 1
    assert httpRequest["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    assert httpRequest["data"]['chat_id'] == chat_id
    assert httpRequest["data"]['reply_to_message_id'] == reply_message_id
    # assert httpRequest["data"]['text'] == ""  # Not testing message content


def test_fail_run_manager_send_message():
    from test_telegram_reporter_class import SessionReplacement

    sessionHandler = SessionReplacement(error_type="KeyboardInterrupt")
    sessionHandler2 = SessionReplacement(error_type="Exception")

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    bot_token = "bot_token"
    chat_id = "chat_id"
    John = RM.RunManager(runPath)

    try:
        John.send_message(2)
    except TypeError as e:
        assert str(e) == ("The `message` must be a str type object, received object of type <class 'int'>")

    try:
        John.send_message("Test message to send", 2)
    except TypeError as e:
        assert str(e) == ("The `reply_to_message_id` must be a str type object or None, received object of type <class 'int'>")

    try:
        John.send_message("Test message to send")
    except RuntimeError as e:
        assert str(e) == ("You can only send messages if the TelegramReporter is configured")

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id)

    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests
    try:
        John.send_message("Test message to send")
    except KeyboardInterrupt as e:
        assert isinstance(e, KeyboardInterrupt)

    John._telegram_reporter._session = sessionHandler2  # To avoid sending actual http requests
    try:
        John.send_message("Test message to send")
    except RuntimeWarning as e:
        assert (
            str(e) == "Could not connect to Telegram to send the message. Reason: RuntimeWarning('Failed sending to "
            "telegram. Reason: Exception()')"
        )

    sessionHandler = SessionReplacement()  # We change the session handler so the del event does not raise an error
    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests


def test_run_manager_edit_message():
    from test_telegram_reporter_class import SessionReplacement

    sessionHandler = SessionReplacement()

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    bot_token = "bot_token"
    chat_id = "chat_id"
    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id)
    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests

    message_to_edit = "message_to_edit"
    message_id = John.edit_message("This is a test message", message_to_edit)

    assert message_id == "This is the message ID"
    httpRequest = sessionHandler.json()
    assert httpRequest["timeout"] == 1
    assert httpRequest["url"] == "https://api.telegram.org/bot{}/editMessageText".format(bot_token)
    assert httpRequest["data"]['chat_id'] == chat_id
    assert httpRequest["data"]['message_id'] == message_to_edit
    # assert httpRequest["data"]['text'] == ""  # Not testing message content


def test_fail_run_manager_edit_message():
    from test_telegram_reporter_class import SessionReplacement

    sessionHandler = SessionReplacement(error_type="KeyboardInterrupt")
    sessionHandler2 = SessionReplacement(error_type="Exception")

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    bot_token = "bot_token"
    chat_id = "chat_id"
    John = RM.RunManager(runPath)

    try:
        John.edit_message(2, 2)
    except TypeError as e:
        assert str(e) == ("The `message` must be a str type object, received object of type <class 'int'>")

    try:
        John.edit_message("Test message to send", 2)
    except TypeError as e:
        assert str(e) == ("The `message_id` must be a str type object, received object of type <class 'int'>")

    try:
        John.edit_message("Test message to send", "message_to_edit")
    except RuntimeError as e:
        assert str(e) == ("You can only send messages if the TelegramReporter is configured")

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id)

    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests
    try:
        John.edit_message("Test message to send", "message_to_edit")
    except KeyboardInterrupt as e:
        assert isinstance(e, KeyboardInterrupt)

    John._telegram_reporter._session = sessionHandler2  # To avoid sending actual http requests
    try:
        John.edit_message("Test message to send", "message_to_edit")
    except RuntimeWarning as e:
        assert (
            str(e) == "Could not connect to Telegram to send the message. Reason: RuntimeWarning('Failed sending to "
            "telegram. Reason: Exception()')"
        )

    sessionHandler = SessionReplacement()  # We change the session handler so the del event does not raise an error
    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests


def test_run_manager_repr():
    from test_telegram_reporter_class import SessionReplacement

    sessionHandler = SessionReplacement()

    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)

    John = RM.RunManager(runPath)
    assert repr(John) == "RunManager({})".format(repr(runPath))
    ensure_clean(runPath)

    bot_token = "bot_token"
    chat_id = "chat_id"
    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id)
    John._telegram_reporter._session = sessionHandler  # To avoid sending actual http requests
    assert repr(John) == "RunManager({}, telegram_bot_token={}, telegram_chat_id={})".format(repr(runPath), repr(bot_token), repr(chat_id))


def test_run_manager_task_ran_successfully():
    tmpdir = tempfile.gettempdir()
    runPath = Path(tmpdir) / "Run0001"
    ensure_clean(runPath)
    John = RM.RunManager(runPath)
    John.create_run(raise_error=True)

    with John.handle_task("myTask") as Oliver:
        (Oliver.task_path / "output_file.txt").touch()

    try:
        with John.handle_task("myTask2") as Leopold:
            (Leopold.task_path / "output_file.txt").touch()
            raise RuntimeError("This is only to exit with a failed task")
    except RuntimeError:
        pass

    assert John.task_ran_successfully("myTask")
    assert not John.task_ran_successfully("myTask2")
    assert not John.task_ran_successfully("myTask3")

    try:
        John.task_ran_successfully(2)
    except TypeError as e:
        assert str(e) == ("The `task_name` must be a str type object, received object of type <class 'int'>")
