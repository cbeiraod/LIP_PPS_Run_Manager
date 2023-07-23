# -*- coding: utf-8 -*-
"""The Run Manager module

Contains classes and functions used to manage the runs and their tasks.

"""

import datetime
import inspect
import json
import shutil
import traceback
import warnings
from pathlib import Path

import humanize

from lip_pps_run_manager import __version__
from lip_pps_run_manager.telegram_reporter import TelegramReporter


def clean_path(path_to_clean: Path) -> Path:
    """Clean a path from dangerous characters

    Some characters are not recommended/supported by a given filesystem.
    To make matters worse, the set of supported characters varies from
    operating system to operating system. In order to make sure this
    code is portable and that things remain compatible, we choose a
    subset of characters on which to limit the paths used. The subset is
    essentially all letters (lower and upper case), all numbers
    augmented with the dot, underscore and dash.

    Parameters
    ----------
    path_to_clean
        The path to the directory to clean

    Raises
    ------
    TypeError
        If the parameter has the wrong type

    Returns
    -------
    Path
        The `path_to_clean` path cleaned of all characters not part of
        the reduced set

    Examples
    --------
    >>> import lip_pps_run_manager.run_manager as RM
    >>> print(RM.clean_path(Path("/tmp/2@#_run")))
    """

    if not isinstance(path_to_clean, Path):
        raise TypeError("The `path_to_clean` must be a Path type object, received object of type {}".format(type(path_to_clean)))

    # SafeCharacters = {
    # 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
    # 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
    # 'W', 'X', 'Y', 'Z',
    # 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
    # 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
    # 'w', 'x', 'y', 'z',
    # '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.',
    # '_', '-'
    # }

    return Path(".")


def run_exists(path_to_directory: Path, run_name: str) -> bool:
    """Check if a given run already exists in a given directory

    Parameters
    ----------
    path_to_directory
        The path to the directory where to check if the run exists

    run_name
        The name of the run to check for

    Raises
    ------
    TypeError
        If either of the parameters has the wrong type

    Returns
    -------
    bool
        `True` if the run already exists, `False` if it does not exist.

    Examples
    --------
    >>> import lip_pps_run_manager.run_manager as RM
    >>> print(RM.run_exists(Path("."), "Run0001"))
    """

    if not isinstance(path_to_directory, Path):
        raise TypeError("The `path_to_directory` must be a Path type object, received object of type {}".format(type(path_to_directory)))
    if not isinstance(run_name, str):
        raise TypeError("The `run_name` must be a str type object, received object of type {}".format(type(run_name)))

    run_path = path_to_directory / run_name

    # TODO: Add check for invalid characters

    return (run_path / 'run_info.txt').is_file()


def create_run(path_to_directory: Path, run_name: str) -> Path:
    """Create a new run in a given directory

    Parameters
    ----------
    path_to_directory
        The path to the directory where to create the run

    run_name
        The name of the run to create

    Raises
    ------
    TypeError
        If either of the parameters has the wrong type

    RuntimeError
        If the run directory already exists

    Returns
    -------
    Path
        The path to the creaated run.

    Examples
    --------
    >>> import lip_pps_run_manager.run_manager as RM
    >>> print(RM.create_run(Path("."), "Run0001"))
    """

    if not isinstance(path_to_directory, Path):
        raise TypeError("The `path_to_directory` must be a Path type object, received object of type {}".format(type(path_to_directory)))
    if not isinstance(run_name, str):
        raise TypeError("The `run_name` must be a str type object, received object of type {}".format(type(run_name)))

    run_path = path_to_directory / run_name

    # TODO: Add check for invalid characters

    if run_path.is_dir():
        raise RuntimeError(
            "Unable to create the run '{}' in '{}' because a directory with that name already exists.".format(run_name, path_to_directory)
        )

    run_path.mkdir(parents=True)

    with open(run_path / "run_info.txt", "w") as out_file:
        out_file.write(
            "This directory contains data for the run '{}', created by the RunManager v{} on {}".format(
                run_name, __version__, datetime.datetime.now()
            )
        )

    return run_path


def load_telegram_config() -> json:
    """Load the config file with the telegram configuration information.

    The function searches for a config file in the working directory
    first with the name 'run_manager_telegram_config.json' and if it
    does not exist, it tries searching for a config file in the home
    directory with the name '.run_manager_telegram_config.json'

    Returns
    -------
    json
        The json representation of the config file

    Examples
    --------
    >>> import lip_pps_run_manager.run_manager as RM
    >>> print(RM.create_run(Path("."), "Run0001"))
    """

    home_config = Path.home() / ".run_manager_telegram_config.json"
    script_config = Path.cwd() / "run_manager_telegram_config.json"

    if script_config.is_file():
        config_file = script_config
    else:  # pragma: no cover
        config_file = home_config

    with config_file.open("r", encoding="utf-8") as file:
        return json.load(file)


class RunManager:
    """Class to manage PPS Runs

    This Class initializes the on disk structures if necessary.

    When using a telegram bot, it is possible to use a configuration
    file to load the secret bot token or/and the unique chat id. Named
    strings are used to identify these quantities, see the example
    config file for the syntax. If the `telegram_bot_name` parameter is
    passed, the `telegram_bot_token` is ignored since it takes
    precedence. The `telegram_chat_name` also takes precedence over the
    `telegram_chat_id`. This helps keep these values secret when using
    the option to automatically back up scripts for each task.

    A default config file should be placed in the home directory and
    have the name '.run_manager_telegram_config.json'. A specific config
    file should be placed in the current running directory and have the
    name 'run_manager_telegram_config.json'

    .. code-block::
        :caption: Example Telegram Bot Configuration File
        :linenos:

        {
            "bots": {
                "bot_name": "bot_token",
                "other_bot_name": "other_bot_token"
            },
            "chats": {
                "chat_name": "chat_id",
                "other_chat_name": "other_chat_id"
            }
        }


    Parameters
    ----------
    path_to_run_directory
        The path to the directory where all the run related information
        is stored. Typically, there will be multiple processing
        steps/tasks applied to a single run and each will have its data
        stored in a single subdirectory.
    telegram_bot_name
        The bot name of the bot to be used to publish the report message
        to telegram. This property takes precedence over
        `telegram_bot_token`, which will be ignored if this parameter is
        passed. A config file should exist with the bot configuration,
        see the example.
    telegram_chat_name
        The chat name of the chat to publish the report messages to
        telegram. This property takes precedence over
        `telegram_chat_id`, which will be ignored if this parameter is
        passed. A config file should exist with the chat configuration,
        see the example.
    telegram_bot_token
        The telegram bot token to use (this value should be a secret, so do not share it) for the `TelegramReporter`, if any.
    telegram_chat_id
        The telegram chat ID the reporter should send messages to

    Raises
    ------
    TypeError
        If a parameter has the incorrect type

    Examples
    --------
    >>> import lip_pps_run_manager as RM
    >>> John = RM.RunManager("Run0001")

    """

    _path_directory = Path(".")
    _bot_name = None
    _chat_name = None
    _bot_token = None
    _chat_id = None
    _telegram_reporter = None
    _run_created = False
    _status_message_id = None
    _in_run_context = False
    _rate_limit = True

    def __init__(
        self,
        path_to_run_directory: Path,
        telegram_bot_name: str = None,
        telegram_chat_name: str = None,
        telegram_bot_token: str = None,
        telegram_chat_id: str = None,
        rate_limit: bool = True,
    ):
        if not isinstance(path_to_run_directory, Path):
            raise TypeError(
                "The `path_to_run_directory` must be a Path type object, received object of type {}".format(type(path_to_run_directory))
            )

        if telegram_bot_name is not None and not isinstance(telegram_bot_name, str):
            raise TypeError(
                "The `telegram_bot_name` must be a str type object or None, received object of type {}".format(type(telegram_bot_name))
            )

        if telegram_chat_name is not None and not isinstance(telegram_chat_name, str):
            raise TypeError(
                "The `telegram_chat_name` must be a str type object or None, received object of type {}".format(type(telegram_chat_name))
            )

        if telegram_bot_token is not None and not isinstance(telegram_bot_token, str):
            raise TypeError(
                "The `telegram_bot_token` must be a str type object, received object of type {}".format(type(telegram_bot_token))
            )

        if telegram_chat_id is not None and not isinstance(telegram_chat_id, str):
            raise TypeError("The `telegram_chat_id` must be a str type object, received object of type {}".format(type(telegram_chat_id)))

        if not isinstance(rate_limit, bool):
            raise TypeError("The `rate_limit` must be a bool type object, received object of type {}".format(type(rate_limit)))

        self._path_directory = path_to_run_directory

        telegram_config = None
        if telegram_bot_name is not None or telegram_chat_name is not None:
            telegram_config = load_telegram_config()

        if telegram_bot_name is not None:
            self._bot_name = telegram_bot_name
            self._bot_token = telegram_config["bots"][telegram_bot_name]
        else:
            self._bot_token = telegram_bot_token

        if telegram_chat_name is not None:
            self._chat_name = telegram_chat_name
            self._chat_id = telegram_config["chats"][telegram_chat_name]
        else:
            self._chat_id = telegram_chat_id

        if self._bot_token is not None and self._chat_id is not None:
            self._rate_limit = rate_limit
        else:
            self._bot_token = None
            self._chat_id = None

    def __repr__(self):
        """Get the python representation of this class"""
        if self._bot_token is None or self._chat_id is None:
            return "RunManager({})".format(repr(self.path_directory))
        else:
            classRepr = "RunManager({}".format(repr(self.path_directory))
            if self._bot_name is not None:
                classRepr += ", telegram_bot_name={}".format(repr(self._bot_name))
            else:
                classRepr += ", telegram_bot_token={}".format(repr(self._bot_token))
            if self._chat_name is not None:
                classRepr += ", telegram_chat_name={}".format(repr(self._chat_name))
            else:
                classRepr += ", telegram_chat_id={}".format(repr(self._chat_id))
            classRepr += ", rate_limit={})".format(self._rate_limit)
            return classRepr

    @property
    def path_directory(self) -> Path:
        """The path directory property getter method

        This method fetches the path_directory internal attribute,
        which contains the path to the directory containing the run
        information for this run.

        Returns
        -------
        Path
            The path to the directory where the run information
            is stored.
        """
        return self._path_directory

    # @path_directory.setter
    # def path_directory(self, value):
    #    """
    #    This is the setter method
    #    where I can check it's not assigned a value < 0
    #    """
    #    self._path_directory = value

    @property
    def data_directory(self) -> Path:
        """The data directory property getter method

        This method fetches the data directory path attribute,
        which points to the path containing the run data of this run.

        Returns
        -------
        Path
            The path to the directory where the data is stored.
        """
        return self._path_directory / "data"

    @property
    def backup_directory(self) -> Path:
        """The backup directory property getter method

        This method fetches the backup directory path attribute,
        which points to the path containing the backup data of this run.

        Returns
        -------
        Path
            The path to the directory where the backup data is stored.
        """
        return self._path_directory / "backup"

    @property
    def run_name(self) -> str:
        """The name of the run property getter method"""
        return self._path_directory.parts[-1]

    def __enter__(self):
        """This is the method that is called when using the "with" syntax"""
        self._in_run_context = True

        if self._bot_token is not None and self._chat_id is not None:
            self._telegram_reporter = TelegramReporter(self._bot_token, self._chat_id, rate_limit=self._rate_limit)
            self._status_message_id = self.send_message("⏰ Preparing for Run {}".format(self.run_name))

        return self

    def __exit__(self, err_type, err_value, err_traceback):
        """This is the method that is called at the end of the block, when using the "with" syntax"""
        if self._telegram_reporter is not None:
            if self._status_message_id is not None:
                self.edit_message("🔰🔰 Start of processing of Run {} 🔰🔰".format(self.run_name), self._status_message_id)
            if all([err is None for err in [err_type, err_value, err_traceback]]):
                self.send_message("✔️✔️ Successfully Finished processing Run {} ✔️✔️".format(self.run_name), self._status_message_id)
            else:
                self.send_message("🚫🚫 Finished processing Run {} with errors 🚫🚫".format(self.run_name), self._status_message_id)

        self._in_run_context = False

    def create_run(self, raise_error: bool = False):
        """Creates a run where this `RunManager` is pointing to.

        Parameters
        ----------
        raise_error
            If `True` a `RuntimeError` is raised if the run already exists.
            If `False` no error is raised whether the run exists or not.

        Raises
        ------
        RuntimeError
            If the `raise_error` parameter is `True` and the run already
            exists or if the run directory already exists.
        Warning
            If any irregularity, during communication with telegram, it is reinterpreted as a warning

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> with RM.RunManager("Run0001") as John
        ...   John.create_run(True)

        The above code should create the Run0001 directory if it doesn't
        exist or exit with a `RuntimeError` if it does.

        """
        if not self._in_run_context:
            raise RuntimeError("Tried calling create_run() while not inside a run context. Use the 'with RunManager as handle' syntax")

        if run_exists(self.path_directory.parent, self.run_name):
            if raise_error:
                raise RuntimeError(
                    "Can not create run '{}', in '{}' because it already exists.".format(self.run_name, self.path_directory.parent)
                )
        else:
            create_run(path_to_directory=self.path_directory.parent, run_name=self.run_name)

        if self._telegram_reporter is not None:
            run_status = "🚀🚀🚀 Started processing Run {}".format(self.run_name)
            if not self._status_message_id:
                self._status_message_id = self.send_message(run_status)
            else:
                self._status_message_id = self.edit_message(run_status, self._status_message_id)

        self._run_created = True

    def handle_task(
        self,
        task_name: str,
        drop_old_data: bool = True,
        backup_python_file: bool = True,
        telegram_loop_iterations: int = None,
        minimum_update_time_seconds: int = 60,
        minimum_warn_time_seconds: int = 60,
    ):
        """Method that creates a handle to a manager for a specific task

        The `TaskManager` that is created is under the current
        `RunManager`.

        Parameters
        ----------
        task_name
            The name of the task which is going to be processed
        drop_old_data
            If a previous directory with the same name as this tasks
            exists, this flag controls whether that data is removed or
            not. Useful when testing and rerunning multiple times, in
            order to ensure that old data from previous runs is cleaned.
        backup_python_file
            If `True` a copy of the current python file will be backed
            up in the task directory. Useful for keeping a log of
            exactly what was done.
        telegram_loop_iterations
            If telegram reporting is enabled, this is the number of
            expected iterations in the processing loop. Use
            `loop_tick()` to keep track of progress during the loop.
        minimum_update_time_seconds
            The minimum time allowed between updates to telegram. This
            parameter is important in order to guarantee that the limits
            imposed by telegram are respected.
        minimum_warn_time_seconds
            The minimum time allowed between warnings to telegram. This
            parameter is important in order to guarantee that the limits
            imposed by telegram are respected.

        Raises
        ------
        TypeError
            If any parameter has the incorrect type

        Returns
        -------
        TaskManager
            The `TaskManager` to handle the task.

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> with RM.RunManager("Run0001") as John:
        ...   John.create_run()
        ...   with John.handle_task("myTask") as taskHandler:
        ...     print("Processing task")

        The above code should create the Run0001 directory and then
        create a subdirectory for the task "myTask".
        """
        if not self._in_run_context:
            raise RuntimeError("Tried calling handle_task() while not inside a run context. Use the 'with RunManager as handle' syntax")

        if not isinstance(task_name, str):
            raise TypeError("The `task_name` must be a str type object, received object of type {}".format(type(task_name)))

        if not isinstance(drop_old_data, bool):
            raise TypeError("The `drop_old_data` must be a bool type object, received object of type {}".format(type(drop_old_data)))

        if not isinstance(backup_python_file, bool):
            raise TypeError(
                "The `backup_python_file` must be a bool type object, received object of type {}".format(type(backup_python_file))
            )

        if telegram_loop_iterations is not None and not isinstance(telegram_loop_iterations, int):
            raise TypeError(
                "The `telegram_loop_iterations` must be a int type object or None, received object of type {}".format(
                    type(telegram_loop_iterations)
                )
            )

        if not isinstance(minimum_update_time_seconds, int):
            raise TypeError(
                "The `minimum_update_time_seconds` must be a int type object, received object of type {}".format(
                    type(minimum_update_time_seconds)
                )
            )

        if not isinstance(minimum_warn_time_seconds, int):
            raise TypeError(
                "The `minimum_warn_time_seconds` must be a int type object, received object of type {}".format(
                    type(minimum_warn_time_seconds)
                )
            )

        if not self._run_created:
            self.create_run(True)

        script_to_backup = None
        if backup_python_file:
            script_to_backup = Path(traceback.extract_stack()[-2].filename)

        TM = TaskManager(
            path_to_run=self.path_directory,
            task_name=task_name,
            drop_old_data=drop_old_data,
            script_to_backup=script_to_backup,
            loop_iterations=telegram_loop_iterations,
            minimum_update_time_seconds=minimum_update_time_seconds,
            minimum_warn_time_seconds=minimum_warn_time_seconds,
        )
        TM._run_created = self._run_created
        TM._in_run_context = self._in_run_context
        if self._telegram_reporter is not None:
            TM._bot_name = self._bot_name
            TM._chat_name = self._chat_name
            TM._bot_token = self._bot_token
            TM._chat_id = self._chat_id
            TM._telegram_reporter = self._telegram_reporter
            TM._status_message_id = self._status_message_id

        return TM

    def get_task_path(self, task_name: str) -> Path:
        """Retrieve the `Path` of a given task

        Parameters
        ----------
        task_name
            The name of the task of which to get the path

        Raises
        ------
        TypeError
            If any parameter has the incorrect type

        Returns
        -------
        Path
            The `Path` to the task directory.

        Warnings
        --------
        The returned directory may or may not exist.

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> John = RM.RunManager("Run0001")
        >>> John.create_run()
        >>> with John.handle_task("myTask") as taskHandler:
        ...   print("Processing task")
        >>> John.get_task_directory("myTask")

        The example above is using the with syntax, which will ensure
        the task directory is created.

        """

        if not isinstance(task_name, str):
            raise TypeError("The `task_name` must be a str type object, received object of type {}".format(type(task_name)))

        return self.path_directory / task_name

    def task_ran_successfully(self, task_name: str) -> bool:
        """Check if a task has ran with success

        Parameters
        ----------
        task_name
            The name of the task to check

        Raises
        ------
        TypeError
            If any parameter has the incorrect type

        Returns
        -------
        bool
            `True` if successfull, `False` otherwise

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> John = RM.RunManager("Run0001")
        >>> John.create_run()
        >>> John.task_ran_successfully("myTask")

        """

        if not isinstance(task_name, str):
            raise TypeError("The `task_name` must be a str type object, received object of type {}".format(type(task_name)))

        success = False

        try:
            with open(self.get_task_path(task_name) / "task_report.txt", "r") as in_file:
                for line in in_file:
                    if "task_status: no errors" in line or "task_status: incomplete" in line:
                        success = True
                        break
        except FileNotFoundError:
            pass

        return success

    def task_completed(self, task_name: str) -> bool:
        """Check if a task has completed with success

        Parameters
        ----------
        task_name
            The name of the task to check

        Raises
        ------
        TypeError
            If any parameter has the incorrect type

        Returns
        -------
        bool
            `True` if completed, `False` otherwise

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> John = RM.RunManager("Run0001")
        >>> John.create_run()
        >>> John.task_completed("myTask")

        """

        if not isinstance(task_name, str):
            raise TypeError("The `task_name` must be a str type object, received object of type {}".format(type(task_name)))

        success = False

        try:
            with open(self.get_task_path(task_name) / "task_report.txt", "r") as in_file:
                for line in in_file:
                    if "task_status: no errors" in line:
                        success = True
                        break
        except FileNotFoundError:
            pass

        return success

    def send_message(self, message: str, reply_to_message_id: str = None):
        """Send a message to telegram

        Parameters
        ----------
        message
            The message to be sent
        reply_to_message_id
            If the message is a reply to another message, place the message ID here

        Raises
        ------
        TypeError
            If any parameter has the incorrect type
        RuntimeError
            If the telegram reporter is not configured
        Warning
            If any irregularity, during communication with telegram, it is reinterpreted as a warning

        Returns
        -------
        message_id: str
            The telegram message id of the message which was just written

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> with RM.RunManager("Run0001", telegram_bot_token="bot_token", telegram_chat_id="chat_id") as John:
        ...   John.create_run()
        ...   John.send_message("This is an example message")

        """
        if not self._in_run_context:
            raise RuntimeError("Tried calling send_message() while not inside a run context. Use the 'with RunManager as handle' syntax")

        if not isinstance(message, str):
            raise TypeError("The `message` must be a str type object, received object of type {}".format(type(message)))

        if reply_to_message_id is not None and not isinstance(reply_to_message_id, str):
            raise TypeError(
                "The `reply_to_message_id` must be a str type object or None, received object of type {}".format(type(reply_to_message_id))
            )

        if self._telegram_reporter is None:
            raise RuntimeError("You can only send messages if the TelegramReporter is configured")

        try:
            self._telegram_response = self._telegram_reporter.send_message(message, reply_to_message_id)
        except Exception as e:
            warnings.warn("Could not connect to Telegram to send the message. Reason: {}".format(repr(e)), category=RuntimeWarning)

        return self._telegram_response['result']['message_id']

    def edit_message(self, message: str, message_id: str):
        """Edit a message previously sent to telegram

        Parameters
        ----------
        message
            The message to be sent
        message_id
            The message ID of the message to edit

        Raises
        ------
        TypeError
            If any parameter has the incorrect type
        RuntimeError
            If the telegram reporter is not configured
        Warning
            If any irregularity, during communication with telegram, it is reinterpreted as a warning

        Returns
        -------
        message_id: str
            The telegram message id of the message which was just written

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> with RM.RunManager("Run0001", telegram_bot_token="bot_token", telegram_chat_id="chat_id") as John:
        ...   John.create_run()
        ...   message_id = John.send_message("This is an example message")
        ...   John.edit_message("This is the edited message", message_id)

        """
        if not self._in_run_context:
            raise RuntimeError("Tried calling edit_message() while not inside a run context. Use the 'with RunManager as handle' syntax")

        if not isinstance(message, str):
            raise TypeError("The `message` must be a str type object, received object of type {}".format(type(message)))

        if not isinstance(message_id, str):
            raise TypeError("The `message_id` must be a str type object, received object of type {}".format(type(message_id)))

        if self._telegram_reporter is None:
            raise RuntimeError("You can only send messages if the TelegramReporter is configured")

        try:
            self._telegram_response = self._telegram_reporter.edit_message(message, message_id)
        except Exception as e:
            warnings.warn("Could not connect to Telegram to send the message. Reason: {}".format(repr(e)), category=RuntimeWarning)

        return self._telegram_response['result']['message_id']

    def copy_file_to(self, source: Path, destination: Path, overwrite: bool = False):
        """Creates a copy of the source file to the destination.

        Parameters
        ----------
        source
            The path to the source file. The file must exist
        destination
            The path to the destination. If the destination does not exist, the
            parent must exist and the file will be created. If the destination
            does exist, it must be a directory and a file with the same name as
            the source will be created. If the destination exists and is a file,
            action will only be taken if the `overwrite` flag is set.
        overwrite
            Whether to overwrite the destination file in case it already exists

        Raises
        ------
        TypeError
            If the type of one of the parameters is not correct
        RuntimeError
            If the `source` does not exist, if the `destination` does not exist
            and the parent directory does not exist or if the `destination`
            does exist and `overwrite` is not set.
        SameFileError
            If `source` and `destination` are the same file, a SameFileError
            will be raised.

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> from pathlib import Path
        >>> with RM.RunManager("Run0001") as John
        ...   John.create_run(True)
        ...   John.copy_file_to(Path("src.file"), Path("copy_of.file"))

        The above code should create a copy of the `src.file` in the
        `copy_of.file`, if the `src.file` exists. If not, a RuntimeError
        will be raised.

        """
        if not isinstance(source, Path):
            raise TypeError(f"The `source` must be a Path type object, received object of type {type(source)} instead")

        if not isinstance(destination, Path):
            raise TypeError(f"The `destination` must be a Path type object, received object of type {type(destination)} instead")

        if not source.exists() or not source.is_file():
            raise RuntimeError("The source file does not exist or it is not a file.")

        if not destination.exists():
            if not destination.parent.exists():
                raise RuntimeError("The parent of the destination file does not exist, unable to create the destination file")
        else:  # Destination exists
            if destination.is_file():
                if not overwrite:
                    raise RuntimeError("The destination file already exists and the overwrite flag is not set")
            else:
                destination = destination / source.name

        shutil.copy(source, destination)

    def backup_file(self, source: Path):
        """Creates a backup of the file inside the run directory under the
        backup subdirectory.

        Parameters
        ----------
        source
            The path to the source file. The file must exist

        Raises
        ------
        TypeError
            If the type of one of the parameters is not correct
        RuntimeError
            If the `source` does not exist.

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> from pathlib import Path
        >>> with RM.RunManager("Run0001") as John
        ...   John.create_run(True)
        ...   John.backup_file(Path("src.file"))

        The above code should create a backup copy of the `src.file` in the
        backup directory of the run, if the `src.file` exists. If not, a
        RuntimeError will be raised.

        """
        if not isinstance(source, Path):
            raise TypeError(f"The `source` must be a Path type object, received object of type {type(source)} instead")

        if not source.exists() or not source.is_file():
            raise RuntimeError("The source file does not exist or it is not a file.")

        backup_path = self.backup_directory
        if not backup_path.exists():
            backup_path.mkdir()

        self.copy_file_to(source, backup_path, overwrite=True)


class TaskManager(RunManager):
    """Class to manage PPS Tasks

    This Class initializes the on disk structures if necessary.

    Parameters
    ----------
    path_to_run
        The path to the directory where all the run related information
        is stored
    task_name
        The name of this task
    drop_old_data
        If a previous directory with the same name as this tasks
        exists, this flag controls whether that data is removed or
        not. Useful when testing and rerunning multiple times, in
        order to ensure that old data from previous runs is cleaned.
    script_to_backup
        `Path` to the script to be backed up to the task directory
    telegram_bot_name
        The bot name of the bot to be used to publish the report message
        to telegram. This property takes precedence over
        `telegram_bot_token`, which will be ignored if this parameter is
        passed. A config file should exist with the bot configuration,
        see the `RunManager` example.
    telegram_chat_name
        The chat name of the chat to publish the report messages to
        telegram. This property takes precedence over
        `telegram_chat_id`, which will be ignored if this parameter is
        passed. A config file should exist with the chat configuration,
        see the `RunManager` example.
    telegram_bot_token
        The telegram bot token to use (this value should be a secret, so
        do not share it) for the `TelegramReporter`, if any.
    telegram_chat_id
        The telegram chat ID the reporter should send messages to
    loop_iterations
        The number of iterations in the loop of the task being
        processed. This value is used mostly for the telegram reporting
        in order to report the current status of the task progress. Use
        `loop_tick()` to keep track of progress during the loop.
    minimum_update_time_seconds
        The minimum time allowed between updates to telegram. This
        parameter is important in order to guarantee that the limits
        imposed by telegram are respected.
    minimum_warn_time_seconds
        The minimum time allowed between warnings to telegram. This
        parameter is important in order to guarantee that the limits
        imposed by telegram are respected.

    Raises
    ------
    TypeError
        If the parameter has the incorrect type
    RuntimeError
        If the paths point to the wrong types (i.e. not a file for a file)
        If a directory which is not the directory of a run is passed

    Examples
    --------
    It is recommended to always use this class through the `RunManager`
    since it is necessary to have the underlying run directories and
    files created. This is what is done in the example below, where the
    `handle_task` method implicitly calls this class.

    >>> import lip_pps_run_manager as RM
    >>> with RM.RunManager("Run0001") as John:
    ...   John.create_run()
    ...   with John.handle_task("myTask") as taskHandler:
    ...     print("Process task here...")

    """

    _task_name = ""
    _drop_old_data = True
    _script_to_backup = Path("")
    _loop_iterations = None
    _processed_iterations = None
    _in_task_context = False
    _task_status_message_id = None
    _minimum_update_time = None
    _minimum_warn_time = None
    _own_run_context = False

    def __init__(
        self,
        path_to_run: Path,
        task_name: str,
        drop_old_data: bool = True,
        script_to_backup: Path = None,
        telegram_bot_name: str = None,
        telegram_chat_name: str = None,
        telegram_bot_token: str = None,
        telegram_chat_id: str = None,
        loop_iterations: int = None,
        minimum_update_time_seconds: int = 60,
        minimum_warn_time_seconds: int = 60,
        rate_limit: bool = True,
    ):
        if not isinstance(path_to_run, Path):
            raise TypeError("The `path_to_run` must be a Path type object, received object of type {}".format(type(path_to_run)))

        if not isinstance(task_name, str):
            raise TypeError("The `task_name` must be a str type object, received object of type {}".format(type(task_name)))

        if not isinstance(drop_old_data, bool):
            raise TypeError("The `drop_old_data` must be a bool type object, received object of type {}".format(type(drop_old_data)))

        if script_to_backup is not None and not isinstance(script_to_backup, Path):
            raise TypeError(
                "The `script_to_backup` must be a Path type object or None, received object of type {}".format(type(script_to_backup))
            )

        if telegram_bot_token is not None and not isinstance(telegram_bot_token, str):
            raise TypeError(
                "The `telegram_bot_token` must be a str type object or None, received object of type {}".format(type(telegram_bot_token))
            )

        if telegram_chat_id is not None and not isinstance(telegram_chat_id, str):
            raise TypeError(
                "The `telegram_chat_id` must be a str type object or None, received object of type {}".format(type(telegram_chat_id))
            )

        if loop_iterations is not None and not isinstance(loop_iterations, int):
            raise TypeError(
                "The `loop_iterations` must be a int type object or None, received object of type {}".format(type(loop_iterations))
            )

        if not isinstance(minimum_update_time_seconds, int):
            raise TypeError(
                "The `minimum_update_time_seconds` must be a int type object, received object of type {}".format(
                    type(minimum_update_time_seconds)
                )
            )

        if not isinstance(minimum_warn_time_seconds, int):
            raise TypeError(
                "The `minimum_warn_time_seconds` must be a int type object, received object of type {}".format(
                    type(minimum_warn_time_seconds)
                )
            )

        if not run_exists(path_to_directory=path_to_run.parent, run_name=path_to_run.parts[-1]):
            raise RuntimeError("The 'path_to_run' ({}) does not look like the directory of a run...".format(path_to_run))

        if script_to_backup is not None and not script_to_backup.is_file():
            raise RuntimeError("The 'script_to_backup', if set, must point to a file. It points to: {}".format(script_to_backup))

        super().__init__(
            path_to_run_directory=path_to_run,
            telegram_bot_name=telegram_bot_name,
            telegram_chat_name=telegram_chat_name,
            telegram_bot_token=telegram_bot_token,
            telegram_chat_id=telegram_chat_id,
            rate_limit=rate_limit,
        )
        self._task_name = task_name
        self._drop_old_data = drop_old_data
        self._script_to_backup = script_to_backup
        self._loop_iterations = loop_iterations
        self._in_task_context = False
        self._minimum_update_time = datetime.timedelta(seconds=float(minimum_update_time_seconds))
        self._minimum_warn_time = datetime.timedelta(seconds=float(minimum_warn_time_seconds))
        if loop_iterations is not None:
            self._processed_iterations = 0

    def __repr__(self):
        """Get the python representation of this class"""
        if self._bot_token is None or self._chat_id is None:
            return (
                "TaskManager({}, {}, drop_old_data={}, script_to_backup={}, "
                "loop_iterations={}, minimum_update_time_seconds={}, "
                "minimum_warn_time_seconds={})".format(
                    repr(self.path_directory),
                    repr(self.task_name),
                    repr(self._drop_old_data),
                    repr(self._script_to_backup),
                    repr(self._loop_iterations),
                    repr(int(self._minimum_update_time.total_seconds())),
                    repr(int(self._minimum_warn_time.total_seconds())),
                )
            )
        else:
            if self._bot_name is not None:
                bot_str = "telegram_bot_name={}".format(repr(self._bot_name))
            else:
                bot_str = "telegram_bot_token={}".format(repr(self._bot_token))

            if self._chat_name is not None:
                chat_str = "telegram_chat_name={}".format(repr(self._chat_name))
            else:
                chat_str = "telegram_chat_id={}".format(repr(self._chat_id))

            return (
                "TaskManager({}, {}, drop_old_data={}, script_to_backup={}, "
                "{}, {}, loop_iterations={}, "
                "minimum_update_time_seconds={}, minimum_warn_time_seconds={}, "
                "rate_limit={})".format(
                    repr(self.path_directory),
                    repr(self.task_name),
                    repr(self._drop_old_data),
                    repr(self._script_to_backup),
                    bot_str,
                    chat_str,
                    repr(self._loop_iterations),
                    repr(int(self._minimum_update_time.total_seconds())),
                    repr(int(self._minimum_warn_time.total_seconds())),
                    repr(self._rate_limit),
                )
            )

    @property
    def task_name(self) -> str:
        """The task name property getter method"""
        return self._task_name

    @property
    def task_path(self) -> Path:
        """The task path property getter method"""
        return self.get_task_path(self.task_name)

    @property
    def processed_iterations(self) -> int:
        """The processed iterations property getter method"""
        return self._processed_iterations

    @property
    def expected_finish_time(self):
        """The time at which the task is expected to be finished"""
        if (
            hasattr(self, "_start_time")
            and self.processed_iterations is not None
            and self.processed_iterations != 0
            and self._loop_iterations is not None
            and self._loop_iterations != 0
        ):
            elapsed_time = datetime.datetime.now() - self._start_time
            return self._start_time + elapsed_time / self.processed_iterations * self._loop_iterations
        return None

    def loop_tick(self, count: int = 1):
        """Increase the internal loop count, it is assumed this method is called at the end of the loop

        When skipping multiple iterations, you can use the count
        parameter to increase the counter for multiple iterations.
        This method is also used internally to do some bookeeping
        operations such as keeping the status message on telegram up to
        date and sending warnings if there have been any. For this
        reason, it is good to call this method with some frequency. If
        the task loop is so long that the frequency of updates is
        deemed too slow, consider calling this method with `count=0` or
        by calling explicitly the `_update_status` method, but keep in
        mind that `_update_status` keeps an eye on when the status was
        last updated, so if it is too soon, no update will be made.

        Parameters
        ----------
        count
            The amount by which to increase the internal loop counter,
            by default, this parameter is set to 1

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> John = RM.RunManager("Run0001")
        >>> John.create_run()
        >>> with John.handle_task("myTask") as taskHandler:
        ...   # Do work
        ...   taskHandler.loop_tick()
        """
        if not self._in_task_context:
            raise RuntimeError("Tried calling loop_tick() while not inside a task context. Use the 'with TaskManager as handle' syntax")

        if not hasattr(self, '_last_update'):
            self._last_update = datetime.datetime.now() - 2 * self._minimum_update_time

        if self._processed_iterations is None:
            self._processed_iterations = 0

        self._processed_iterations += count
        if self._loop_iterations is not None and self.processed_iterations > self._loop_iterations:
            self.warn(
                "The number of processed iterations has exceeded the "
                "set number of iterations.\n  - Expected {} iterations;"
                "\n  - Processed {} iterations".format(self._loop_iterations, self._processed_iterations)
            )

        self._update_status()
        self._send_warnings()

    def _update_status(self):
        """Internal method to update the status of the task on the telegram status message"""
        if not self._in_task_context:
            raise RuntimeError(
                "Tried calling _update_status() while not inside a task context. Use the 'with TaskManager as handle' syntax"
            )

        if self._telegram_reporter is not None:
            create_status = False
            if not hasattr(self, "_task_status_message_id") or self._task_status_message_id is None:
                create_status = True
            if not hasattr(self, '_last_update'):
                self._last_update = datetime.datetime.now() - 2 * self._minimum_update_time
            elapsed_time = datetime.datetime.now() - self._last_update
            if create_status or elapsed_time >= self._minimum_update_time:
                self._last_update = datetime.datetime.now()
                new_status = "▶️▶️ Processing task {} of run {} 🍀\n".format(
                    self.task_name, self.run_name
                )  # Four leaf clover is to wish good luck on the completion of the task
                new_status += "     Started {}\n".format(self._start_time.strftime("%Y-%m-%d %H:%M"))
                if self.expected_finish_time is not None:
                    new_status += "     Expected finish: {}\n".format(self.expected_finish_time.strftime("%Y-%m-%d %H:%M"))
                    new_status += "     Remaining time: {}\n\n".format(
                        humanize.naturaltime(datetime.datetime.now() - self.expected_finish_time)
                    )
                    new_status += "     Progress: {} % ({}/{})\n\n\n".format(
                        int(float(self.processed_iterations) / self._loop_iterations * 100),
                        int(self.processed_iterations),
                        int(self._loop_iterations),
                    )
                else:
                    new_status += "     Unknown expected finish time and remaining time\n\n"
                    if self.processed_iterations is not None:
                        if self._loop_iterations is None or self._loop_iterations == 0:
                            new_status += "     Progress: {} out of an unknown number of iterations\n\n\n".format(self.processed_iterations)
                        else:
                            new_status += "     Progress: {} out of {} iterations\n\n\n".format(
                                self.processed_iterations, self._loop_iterations
                            )
                new_status += "Last update of this message: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

                if create_status:
                    self._task_status_message_id = self.send_message(new_status, self._status_message_id)
                else:
                    self.edit_message(new_status, self._task_status_message_id)

    def set_completed(self):
        """Set the task as if it had completed

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> John = RM.RunManager("Run0001")
        >>> John.create_run()
        >>> with John.handle_task("myTask") as taskHandler:
        ...   # Do work
        ...   taskHandler.set_completed()
        """
        if not self._in_task_context:
            raise RuntimeError("Tried calling set_completed() while not inside a task context. Use the 'with TaskManager as handle' syntax")

        self._processed_iterations = self._loop_iterations

    def clean_task_directory(self):
        """Clean directory of task of all previous data

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> John = RM.RunManager("Run0001")
        >>> John.create_run()
        >>> with John.handle_task("myTask") as taskHandler:
        ...   (taskHandler.task_path/"testFile.tmp").touch()
        ...   taskHandler.clean_task_directory()
        ...   print((taskHandler.task_path/"testFile.tmp").is_file())
        """
        for p in self.task_path.iterdir():
            if p.is_file():
                p.unlink()
            else:  # p.is_dir():
                shutil.rmtree(p)

    def __enter__(self):
        """This is the method that is called when using the "with" syntax"""
        if hasattr(self, "_already_processed"):
            raise RuntimeError("Once a task has processed its data, it can not be processed again. Use a new task")

        if self._drop_old_data and self.task_path.is_dir():
            self.clean_task_directory()
        self.task_path.mkdir(exist_ok=True)

        frame = inspect.currentframe()
        self._locals_on_call = frame.f_back.f_locals

        self._in_task_context = True
        if not self._in_run_context:
            self._own_run_context = True
            self._in_run_context = True
            if self._bot_token is not None and self._chat_id is not None:
                self._telegram_reporter = TelegramReporter(self._bot_token, self._chat_id, rate_limit=self._rate_limit)

        self._start_time = datetime.datetime.now()
        if self._telegram_reporter is not None:
            if self._loop_iterations is None:
                self._task_status_message_id = self.send_message(
                    "Started processing task {} of run {}.\nAn update should come soon".format(self.task_name, self.run_name),
                    self._status_message_id,
                )
            else:
                self._task_status_message_id = self.send_message(
                    "Started processing task {} of run {}.\nIt has {} iterations.\nAn update should come soon".format(
                        self.task_name, self.run_name, self._loop_iterations
                    ),
                    self._status_message_id,
                )

        return self

    def __exit__(self, err_type, err_value, err_traceback):
        """This is the method that is called at the end of the block, when using the "with" syntax"""
        self._already_processed = True

        self._in_task_context = False

        with open(self.task_path / "task_report.txt", "w", encoding="utf8") as out_file:
            if all([err is None for err in [err_type, err_value, err_traceback]]):
                status_message = "no errors"
                if self._loop_iterations is not None and self._loop_iterations > 0:
                    if self._processed_iterations != self._loop_iterations:
                        status_message = "incomplete"
                out_file.write("task_status: {}\n".format(status_message))
                out_file.write("Task completed successfully with no errors\n")
                out_file.write("The task finished running on: {}.\n".format(datetime.datetime.now()))
            else:
                out_file.write("task_status: there were errors\n")
                out_file.write("Task could not be completed because there were errors\n")
                out_file.write("The task finished running on: {}\n".format(datetime.datetime.now()))
                out_file.write("--------\n")
                traceback.print_tb(err_traceback, file=out_file)
                out_file.write("\n")
                out_file.write("{}: {}\n".format(err_type.__name__, err_value))
            out_file.write("\nLIP-PPS-Run-Manager v {} was used as the managing backend.\n".format(__version__))

        if self._script_to_backup is not None:
            if self._script_to_backup.is_file():
                outPath = self.task_path / ("backup.{}".format(self._script_to_backup.parts[-1]))
                with open(outPath, "w", encoding="utf8") as out_file:
                    out_file.write("# ------------------------------------------------------------------------------------------------\n")
                    out_file.write("# This is an automatic backup of the script that processed this task, made at the end of the task.\n")
                    out_file.write("# Please note that the same script may process multiple tasks, so it may show up multiple times.\n")
                    out_file.write("# The original location and name of the script was {}.\n".format(self._script_to_backup))
                    out_file.write("# LIP-PPS-Run-Manager v {} was used as the managing backend.\n".format(__version__))
                    out_file.write("# The backup was created on {}.\n".format(datetime.datetime.now()))
                    out_file.write("# A copy of all the local variables at the time the __enter__ method of the task started:\n")
                    for key in self._locals_on_call:
                        out_file.write("#   {}: {}\n".format(key, repr(self._locals_on_call[key])))
                    out_file.write("# ------------------------------------------------------------------------------------------------\n")
                    with open(self._script_to_backup, "r", encoding="utf8") as in_file:
                        for line in in_file:
                            out_file.write(line)
                # shutil.copyfile(self._script_to_backup, self.task_path / ("backup.{}".format(self._script_to_backup.parts[-1])))
            else:
                raise RuntimeError("Somehow you are trying to backup a file that does not exist")

        if self._own_run_context:
            self._in_run_context = False

    def warn(self, message: str):
        """Send a warning to telegram

        Send the warning as a reply to the original status message. If
        the warnings are sent with less than `minimum_warn_time_seconds`
        parameter, the messages are stored and sent later.

        Parameters
        ----------
        message
            The warning message to be sent

        Raises
        ------
        TypeError
            If the parameter has the incorrect type
        """
        if not isinstance(message, str):
            raise TypeError("The `message` must be a str type object, received object of type {}".format(type(message)))

        if not hasattr(self, "_accumulated_warnings"):
            self._accumulated_warnings = {}

        if message not in self._accumulated_warnings:
            self._accumulated_warnings[message] = 1
        else:
            self._accumulated_warnings[message] += 1

        self._send_warnings()

    def _send_warnings(self):
        """Actually send the warnings to telegram, multiple warnings are combined into one"""
        if not hasattr(self, "_accumulated_warnings") or self._accumulated_warnings == {}:
            return

        if self._telegram_reporter is not None:
            if not hasattr(self, "_task_status_message_id") or self._task_status_message_id is None:
                return
            if not hasattr(self, "_last_warn"):
                self._last_warn = datetime.datetime.now() - 2 * self._minimum_warn_time
            elapsed_time = datetime.datetime.now() - self._last_warn
            if elapsed_time >= self._minimum_warn_time:
                self._last_warn = datetime.datetime.now()
                if len(self._accumulated_warnings) == 1:
                    message_to_send = list(self._accumulated_warnings.keys())[0]
                    if self._accumulated_warnings[message_to_send] > 1:
                        message_to_send = (
                            "Received the following warning {} times in the last {}:\n".format(
                                self._accumulated_warnings[message_to_send], humanize.naturaldelta(self._minimum_warn_time)
                            )
                            + message_to_send
                        )
                else:
                    message_to_send = "Several warnings received in the last {}\n".format(humanize.naturaldelta(self._minimum_warn_time))
                    for msg, count in self._accumulated_warnings.items():
                        message_to_send += "\n----------------------------------\n"
                        if count > 1:
                            message_to_send += "Received the following warning {} times:\n".format(count)
                        message_to_send += msg
                self.send_message(message_to_send, self._task_status_message_id)
                self._accumulated_warnings = {}
        else:
            self._supposedly_just_sent_warnings = self._accumulated_warnings  # Do this just because of the testing
            self._accumulated_warnings = {}

    def backup_file(self, source: Path):
        """Creates a backup of the source file inside the task directory.

        Parameters
        ----------
        source
            The path to the source file. The file must exist

        Raises
        ------
        TypeError
            If the type of one of the parameters is not correct
        RuntimeError
            If the `source` does not exist.

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> from pathlib import Path
        >>> with RM.RunManager("Run0001") as John
        ...   John.create_run(True)
        ...   John.backup_file(Path("src.file"))

        TODO: Fix this examples

        The above code should create a backup copy of the `src.file` in the
        backup directory of the run, if the `src.file` exists. If not, a
        RuntimeError will be raised.

        """
        if not isinstance(source, Path):
            raise TypeError(f"The `source` must be a Path type object, received object of type {type(source)} instead")

        if not source.exists() or not source.is_file():
            raise RuntimeError("The source file does not exist or it is not a file.")

        backup_path = self.task_path

        self.copy_file_to(source, backup_path / (source.name + ".bak"), overwrite=True)
