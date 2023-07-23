import datetime
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from test_telegram_reporter_class import SessionReplacement

import lip_pps_run_manager as RM


def ensure_clean(path: Path):  # pragma: no cover
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def ensure_exists(path: Path):  # pragma: no cover
    if not path.exists():
        path.mkdir()


def prepare_config_file(bot_name, bot_token, chat_name, chat_id):  # pragma: no cover
    config_file = Path.cwd() / "run_manager_telegram_config.json"
    with config_file.open("w", encoding="utf-8") as file:
        file.write("{\n")
        file.write('  "bots": {\n')
        file.write('    "{}": "{}"\n'.format(bot_name, bot_token))
        file.write("  },\n")
        file.write('  "chats": {\n')
        file.write('    "{}": "{}"\n'.format(chat_name, chat_id))
        file.write("  }\n")
        file.write("}\n")

    return config_file


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, rate_limit=False)

    assert John._path_directory == runPath
    assert John.path_directory == runPath
    assert John.data_directory == runPath / "data"
    assert John.backup_directory == runPath / "backup"
    assert John.run_name == run_name
    assert John._bot_token is None
    assert John._chat_id is None
    assert John._rate_limit


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_with_bot_ids():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    assert John._bot_token == bot_token
    assert John._chat_id == chat_id
    assert John._rate_limit == rate_limit


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_with_bot_names():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_name = "bot_name"
    chat_name = "chat_name"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    config_file = prepare_config_file(bot_name, bot_token, chat_name, chat_id)

    John = RM.RunManager(runPath, telegram_bot_name=bot_name, telegram_chat_name=chat_name, rate_limit=rate_limit)

    assert John._bot_name == bot_name
    assert John._chat_name == chat_name
    assert John._rate_limit == rate_limit
    assert John._bot_token == bot_token
    assert John._chat_id == chat_id

    config_file.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_with_only_bot_name():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_name = "bot_name"
    chat_name = "chat_name"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    config_file = prepare_config_file(bot_name, bot_token, chat_name, chat_id)

    John = RM.RunManager(runPath, telegram_bot_name=bot_name, telegram_chat_id=chat_id, rate_limit=rate_limit)

    assert John._bot_name == bot_name
    assert John._rate_limit == rate_limit
    assert John._bot_token == bot_token
    assert John._chat_id == chat_id

    config_file.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_with_only_chat_name():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_name = "bot_name"
    chat_name = "chat_name"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    config_file = prepare_config_file(bot_name, bot_token, chat_name, chat_id)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_name=chat_name, rate_limit=rate_limit)

    assert John._chat_name == chat_name
    assert John._rate_limit == rate_limit
    assert John._bot_token == bot_token
    assert John._chat_id == chat_id

    config_file.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_partial_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token)

    assert John._bot_token is None
    assert John._chat_id is None

    David = RM.RunManager(runPath, telegram_chat_id=chat_id)

    assert David._bot_token is None
    assert David._chat_id is None


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_path():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    try:
        RM.RunManager(2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `path_to_run_directory` must be a Path type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_bot_name():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    try:
        RM.RunManager(runPath, telegram_bot_name=2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `telegram_bot_name` must be a str type object or None, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_chat_name():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    try:
        RM.RunManager(runPath, telegram_chat_name=2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `telegram_chat_name` must be a str type object or None, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_bot_token():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    try:
        RM.RunManager(runPath, telegram_bot_token=2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `telegram_bot_token` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_chat_id():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    try:
        RM.RunManager(runPath, telegram_chat_id=2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `telegram_chat_id` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_init_bad_type_rate_limit():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    try:
        RM.RunManager(runPath, rate_limit=2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `rate_limit` must be a bool type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_repr_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    assert repr(John) == "RunManager({})".format(repr(runPath))


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_repr_with_bot_ids():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    assert repr(John) == "RunManager({}, telegram_bot_token={}, telegram_chat_id={}, rate_limit={})".format(
        repr(runPath), repr(bot_token), repr(chat_id), repr(rate_limit)
    )


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_repr_with_bot_names():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_name = "bot_name"
    chat_name = "chat_name"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    config_file = prepare_config_file(bot_name, bot_token, chat_name, chat_id)

    John = RM.RunManager(runPath, telegram_bot_name=bot_name, telegram_chat_name=chat_name, rate_limit=rate_limit)

    assert repr(John) == "RunManager({}, telegram_bot_name={}, telegram_chat_name={}, rate_limit={})".format(
        repr(runPath), repr(bot_name), repr(chat_name), repr(rate_limit)
    )

    config_file.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_get_task_path():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    assert John.get_task_path(task_name) == runPath / task_name


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_get_task_path_bad_type():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    try:
        John.get_task_path(2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `task_name` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_ran_successfully_bad_type():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    try:
        John.task_ran_successfully(2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `task_name` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_ran_successfully_no_dir():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    assert not John.task_ran_successfully(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_ran_successfully_no_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    assert not John.task_ran_successfully(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_ran_successfully_empty_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    (runPath / task_name / "task_report.txt").touch()  # Create the empty file for the task status
    assert not John.task_ran_successfully(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_ran_successfully_fail_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    with (runPath / task_name / "task_report.txt").open("w", encoding="utf8") as task_file:  # Create the task status file
        task_file.write("task_status: there were errors\n")
        task_file.write("Task could not be completed because there were errors\n")
        task_file.write("The task finished running on: {}\n".format(datetime.datetime.now()))
        task_file.write("--------\n")
    assert not John.task_ran_successfully(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_ran_successfully_incompleted_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    with (runPath / task_name / "task_report.txt").open("w", encoding="utf8") as task_file:  # Create the task status file
        task_file.write("task_status: incomplete\n")
        task_file.write("Task completed successfully with no errors\n")
        task_file.write("The task finished running on: {}.\n".format(datetime.datetime.now()))
    assert John.task_ran_successfully(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_ran_successfully_completed_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    with (runPath / task_name / "task_report.txt").open("w", encoding="utf8") as task_file:  # Create the task status file
        task_file.write("task_status: no errors\n")
        task_file.write("Task completed successfully with no errors\n")
        task_file.write("The task finished running on: {}.\n".format(datetime.datetime.now()))
    assert John.task_ran_successfully(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_completed_bad_type():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    try:
        John.task_completed(2)
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except TypeError as e:
        assert str(e) == "The `task_name` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_completed_no_dir():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    assert not John.task_completed(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_completed_no_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    assert not John.task_completed(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_completed_empty_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    (runPath / task_name / "task_report.txt").touch()  # Create the empty file for the task status
    assert not John.task_completed(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_completed_fail_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    with (runPath / task_name / "task_report.txt").open("w", encoding="utf8") as task_file:  # Create the task status file
        task_file.write("task_status: there were errors\n")
        task_file.write("Task could not be completed because there were errors\n")
        task_file.write("The task finished running on: {}\n".format(datetime.datetime.now()))
        task_file.write("--------\n")
    assert not John.task_completed(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_completed_incompleted_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    with (runPath / task_name / "task_report.txt").open("w", encoding="utf8") as task_file:  # Create the task status file
        task_file.write("task_status: incomplete\n")
        task_file.write("Task completed successfully with no errors\n")
        task_file.write("The task finished running on: {}.\n".format(datetime.datetime.now()))
    assert not John.task_completed(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_task_completed_completed_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    task_name = "myTask"
    (runPath / task_name).mkdir(parents=True)  # Create the directory for the task
    with (runPath / task_name / "task_report.txt").open("w", encoding="utf8") as task_file:  # Create the task status file
        task_file.write("task_status: no errors\n")
        task_file.write("Task completed successfully with no errors\n")
        task_file.write("The task finished running on: {}.\n".format(datetime.datetime.now()))
    assert John.task_completed(task_name)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    assert not John._in_run_context
    with John as john:
        assert john._in_run_context
        assert john._telegram_reporter is None


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_enter_with_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    assert John._telegram_reporter is None
    assert John._status_message_id is None
    with John as john:
        assert john._telegram_reporter is not None
        assert john._status_message_id is not None

        # Also check if the correct message is sent
        telegram_message = "⏰ Preparing for Run {}".format(john.run_name)
        httpRequest = john._telegram_reporter._session.json()
        assert httpRequest["data"]['text'] == telegram_message


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    with John as john:
        assert john._in_run_context
    assert not John._in_run_context


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_with_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    with John:
        pass

    httpRequest = John._telegram_reporter._session.json()

    telegram_successful_end_message = "✔️✔️ Successfully Finished processing Run {} ✔️✔️".format(John.run_name)
    assert httpRequest["data"]['text'] == telegram_successful_end_message

    telegram_updated_status_message = "🔰🔰 Start of processing of Run {} 🔰🔰".format(John.run_name)
    assert httpRequest["previous message"]["data"]['text'] == telegram_updated_status_message


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_with_bot_no_status():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    with John as john:
        john._status_message_id = None
        john._telegram_reporter._session._clear()

    httpRequest = John._telegram_reporter._session.json()

    telegram_successful_end_message = "✔️✔️ Successfully Finished processing Run {} ✔️✔️".format(John.run_name)
    assert httpRequest["data"]['text'] == telegram_successful_end_message

    assert httpRequest["previous message"] == {}


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_exit_with_bot_exception():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    try:
        with John:
            raise RuntimeError("test")
    except RuntimeError:
        pass

    httpRequest = John._telegram_reporter._session.json()

    telegram_successful_end_message = "🚫🚫 Finished processing Run {} with errors 🚫🚫".format(John.run_name)
    assert httpRequest["data"]['text'] == telegram_successful_end_message


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_create_run_outside_context():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    try:
        John.create_run()
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except RuntimeError as e:
        assert str(e) == "Tried calling create_run() while not inside a run context. Use the 'with RunManager as handle' syntax"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_create_run_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    assert not John._run_created
    assert not runPath.is_dir()
    with John as john:
        john.create_run()
        assert john._run_created
        assert runPath.is_dir()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_create_run_no_bot_repeated_calls():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath)

    with John as john:
        john.create_run()

        john._run_created = False
        john.create_run()
        assert john._run_created

        try:
            john.create_run(raise_error=True)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "Can not create run '{}', in '{}' because it already exists.".format(john.run_name, tmpdir)


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_create_run_with_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        John.create_run()

        httpRequest = John._telegram_reporter._session.json()
        telegram_message = "🚀🚀🚀 Started processing Run {}".format(John.run_name)
        assert httpRequest["data"]['text'] == telegram_message


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_create_run_with_bot_no_status():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        John._status_message_id = None
        John.create_run()

        httpRequest = John._telegram_reporter._session.json()
        telegram_message = "🚀🚀🚀 Started processing Run {}".format(John.run_name)
        assert httpRequest["data"]['text'] == telegram_message


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_message_outside_context():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    try:
        John.send_message("Test message")
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except RuntimeError as e:
        assert str(e) == "Tried calling send_message() while not inside a run context. Use the 'with RunManager as handle' syntax"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_edit_message_outside_context():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    try:
        John.edit_message("Test message", "message to edit")
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except RuntimeError as e:
        assert str(e) == "Tried calling edit_message() while not inside a run context. Use the 'with RunManager as handle' syntax"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_message_bad_type_message():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.send_message(2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `message` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_edit_message_bad_type_message():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.edit_message(2, "message id")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `message` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_message_bad_type_reply_to_message_id():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.send_message("Test message", 2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `reply_to_message_id` must be a str type object or None, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_edit_message_bad_type_message_id():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.edit_message("Test message", 2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `message_id` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_message_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath) as John:
        try:
            John.send_message("Test message")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "You can only send messages if the TelegramReporter is configured"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_edit_message_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath) as John:
        try:
            John.edit_message("Test message", "message id")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "You can only send messages if the TelegramReporter is configured"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_message_with_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        test_message = "This is the test message"
        message_id = "The message ID to reply to"

        John.send_message(test_message, message_id)

        httpRequest = John._telegram_reporter._session.json()
        assert httpRequest["data"]['text'] == test_message
        assert httpRequest["data"]['reply_to_message_id'] == message_id


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_edit_message_with_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        test_message = "This is the test message"
        message_id = "The message ID to reply to"

        John.edit_message(test_message, message_id)

        httpRequest = John._telegram_reporter._session.json()
        assert httpRequest["data"]['text'] == test_message
        assert httpRequest["data"]['message_id'] == message_id


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_message_with_bot_exception():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        test_message = "This is the test message"
        message_id = "The message ID to reply to"

        John._telegram_reporter._session._set_error_type(error_type="Exception")

        try:
            John.send_message(test_message, message_id)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeWarning as e:
            assert (
                str(e) == "Could not connect to Telegram to send the message. "
                "Reason: RuntimeWarning('Failed sending to telegram. "
                "Reason: Exception()')"
            )

        John._telegram_reporter._session._set_error_type()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_send_message_with_bot_keyboard_interrupt():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        test_message = "This is the test message"
        message_id = "The message ID to reply to"

        John._telegram_reporter._session._set_error_type(error_type="KeyboardInterrupt")

        try:
            John.send_message(test_message, message_id)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except KeyboardInterrupt as e:
            assert isinstance(e, KeyboardInterrupt)

        John._telegram_reporter._session._set_error_type()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_edit_message_with_bot_exception():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        test_message = "This is the test message"
        message_id = "The message ID to reply to"

        John._telegram_reporter._session._set_error_type(error_type="Exception")

        try:
            John.edit_message(test_message, message_id)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeWarning as e:
            assert (
                str(e) == "Could not connect to Telegram to send the message. "
                "Reason: RuntimeWarning('Failed sending to telegram. "
                "Reason: Exception()')"
            )

        John._telegram_reporter._session._set_error_type()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_edit_message_with_bot_keyboard_interrupt():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        test_message = "This is the test message"
        message_id = "The message ID to reply to"

        John._telegram_reporter._session._set_error_type(error_type="KeyboardInterrupt")

        try:
            John.edit_message(test_message, message_id)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except KeyboardInterrupt as e:
            assert isinstance(e, KeyboardInterrupt)

        John._telegram_reporter._session._set_error_type()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_outside_context():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    John = RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit)

    try:
        John.handle_task("myTask")
        raise Exception("Passed through a fail condition without failing")  # pragma: no cover
    except RuntimeError as e:
        assert str(e) == "Tried calling handle_task() while not inside a run context. Use the 'with RunManager as handle' syntax"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_bad_type_task_name():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.handle_task(2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `task_name` must be a str type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_bad_type_drop_old_data():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.handle_task("myTask", drop_old_data=2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `drop_old_data` must be a bool type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_bad_type_backup_python_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.handle_task("myTask", backup_python_file=2)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `backup_python_file` must be a bool type object, received object of type <class 'int'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_bad_type_telegram_loop_iterations():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.handle_task("myTask", telegram_loop_iterations="2")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `telegram_loop_iterations` must be a int type object or None, received object of type <class 'str'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_bad_type_minimum_update_time_seconds():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.handle_task("myTask", minimum_update_time_seconds="2")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `minimum_update_time_seconds` must be a int type object, received object of type <class 'str'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_bad_type_minimum_warn_time_seconds():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        try:
            John.handle_task("myTask", minimum_warn_time_seconds="2")
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `minimum_warn_time_seconds` must be a int type object, received object of type <class 'str'>"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_run_creation():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath) as John:
        assert not John._run_created
        John.handle_task("myTask1")
        assert John._run_created
        John.handle_task("myTask2")
        assert John._run_created


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_script_backup():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath) as John:
        David = John.handle_task("myTask1", backup_python_file=True)
        assert David._script_to_backup is not None

        Joan = John.handle_task("myTask2", backup_python_file=False)
        assert Joan._script_to_backup is None


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_no_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath) as John:
        David = John.handle_task("myTask1", backup_python_file=True)

        assert isinstance(David, RM.TaskManager)
        assert David._run_created == John._run_created
        assert David._in_run_context == John._in_run_context


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_handle_task_with_bot():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    with RM.RunManager(runPath, telegram_bot_token=bot_token, telegram_chat_id=chat_id, rate_limit=rate_limit) as John:
        David = John.handle_task("myTask1", backup_python_file=True)

        assert David._bot_token == John._bot_token
        assert David._chat_id == John._chat_id
        assert David._telegram_reporter == John._telegram_reporter
        assert David._status_message_id == John._status_message_id


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_destination_is_file_to_create():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"
    destination = runPath / "copied_file.txt"

    assert not destination.exists()
    assert not source.exists()

    with open(source, "w") as file:
        file.write("Hello!\n")
        file.write("This is a test file\n")

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)

        John.copy_file_to(source, destination)

        assert destination.exists()

        import filecmp

        assert filecmp.cmp(source, destination)

    source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_destination_is_dir():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"
    destination = runPath

    assert not source.exists()

    with open(source, "w") as file:
        file.write("Hello!\n")
        file.write("This is a test file\n")

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        assert destination.exists()
        assert destination.is_dir()

        John.copy_file_to(source, destination)

        assert (destination / "test_in_file.txt").exists()

        import filecmp

        assert filecmp.cmp(source, (destination / "test_in_file.txt"))

    source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_destination_is_file_to_overwrite():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"
    destination = runPath / "copied_file.txt"

    assert not destination.exists()
    assert not source.exists()

    with open(source, "w") as file:
        file.write("Hello!\n")
        file.write("This is a test file\n")

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)

        with open(destination, "w") as file:
            file.write("This is a mostly empty file.\n")

        assert destination.exists()

        John.copy_file_to(source, destination, overwrite=True)

        assert destination.exists()

        import filecmp

        assert filecmp.cmp(source, destination)

    source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_destination_is_file_no_overwrite():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"
    destination = runPath / "copied_file.txt"

    assert not destination.exists()
    assert not source.exists()

    with open(source, "w") as file:
        file.write("Hello!\n")
        file.write("This is a test file\n")

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)

        with open(destination, "w") as file:
            file.write("This is a mostly empty file.\n")

        assert destination.exists()

        try:
            John.copy_file_to(source, destination)
        except RuntimeError as e:
            assert str(e) == "The destination file already exists and the overwrite flag is not set"

    source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_bad_type_source():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = 2
    destination = runPath / "copied_file.txt"

    assert not destination.exists()

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        try:
            John.copy_file_to(source, destination)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `source` must be a Path type object, received object of type <class 'int'> instead"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_bad_type_destination():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"
    destination = 2

    assert not source.exists()

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        try:
            John.copy_file_to(source, destination)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `destination` must be a Path type object, received object of type <class 'int'> instead"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_source_does_not_exist():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"
    destination = runPath / "copied_file.txt"

    assert not destination.exists()
    assert not source.exists()

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        try:
            John.copy_file_to(source, destination)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "The source file does not exist or it is not a file."


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_source_is_not_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir)
    destination = runPath / "copied_file.txt"

    assert not destination.exists()

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        try:
            John.copy_file_to(source, destination)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "The source file does not exist or it is not a file."


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_copy_file_to_destination_parent_does_not_exist():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"
    destination = runPath / "this_dir_does_not_exist" / "copied_file.txt"

    assert not destination.exists()
    assert not destination.parent.exists()
    assert not source.exists()

    with open(source, "w") as file:
        file.write("Hello!\n")
        file.write("This is a test file\n")

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        try:
            John.copy_file_to(source, destination)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "The parent of the destination file does not exist, unable to create the destination file"

    source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"

    assert not source.exists()

    with open(source, "w") as file:
        file.write("Hello!\n")
        file.write("This is a test file\n")

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)

        assert not John.backup_directory.exists()

        John.backup_file(source)

        assert John.backup_directory.exists()

        assert (John.backup_directory / source.name).exists()

        import filecmp

        assert filecmp.cmp(source, (John.backup_directory / source.name))

    source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file_backup_dir_exists():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"

    assert not source.exists()

    with open(source, "w") as file:
        file.write("Hello!\n")
        file.write("This is a test file\n")

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)

        assert not John.backup_directory.exists()
        John.backup_directory.mkdir()
        assert John.backup_directory.exists()

        John.backup_file(source)

        assert (John.backup_directory / source.name).exists()

        import filecmp

        assert filecmp.cmp(source, (John.backup_directory / source.name))

    source.unlink()


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file_bad_type_source():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = 2

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)

        try:
            John.backup_file(source)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except TypeError as e:
            assert str(e) == "The `source` must be a Path type object, received object of type <class 'int'> instead"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file_source_does_not_exist():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir) / "test_in_file.txt"

    assert not source.exists()

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        try:
            John.backup_file(source)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "The source file does not exist or it is not a file."


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_backup_file_source_is_not_file():
    tmpdir = tempfile.gettempdir()
    run_name = "Run0001"
    runPath = Path(tmpdir) / run_name
    ensure_clean(runPath)

    source = Path(tmpdir)

    with RM.RunManager(runPath) as John:
        John.create_run(raise_error=True)
        try:
            John.backup_file(source)
            raise Exception("Passed through a fail condition without failing")  # pragma: no cover
        except RuntimeError as e:
            assert str(e) == "The source file does not exist or it is not a file."
