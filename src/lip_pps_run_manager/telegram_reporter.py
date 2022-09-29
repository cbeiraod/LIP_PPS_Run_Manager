# -*- coding: utf-8 -*-
"""The Telegram Reporter module

Contains classes and functions used to manage bots to report things to telegram.

"""

import requests


class TelegramReporter:
    """Class to report to telegram

    Parameters
    ----------
    bot_token
        The telegram bot token to use (this value should be a secret, so do not share it)
    chat_id
        The telegram chat ID the reporter should send messages to

    Attributes
    ----------
    path_directory

    Raises
    ------
    TypeError
        If the parameter has the incorrect type

    Examples
    --------
    >>> import lip_pps_run_manager as RM
    >>> John = RM.RunManager("Run0001")

    """

    _bot_token = None
    _chat_id = None
    _session = None

    def __init__(self, bot_token: str, chat_id: str):

        if not isinstance(bot_token, str):
            raise TypeError("The `bot_token` must be a str type object, received object of type {}".format(type(bot_token)))

        if not isinstance(chat_id, str):
            raise TypeError("The `chat_id` must be a str type object, received object of type {}".format(type(chat_id)))

        self._bot_token = bot_token
        self._chat_id = chat_id
        self._session = requests.Session()

    @property
    def bot_token(self) -> str:
        """The token of the telegram bot property getter method"""
        return self._bot_token

    @property
    def chat_id(self) -> str:
        """The chat ID property getter method"""
        return self._chat_id
