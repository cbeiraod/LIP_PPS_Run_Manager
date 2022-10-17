# -*- coding: utf-8 -*-
"""The Telegram Reporter module

Contains classes and functions used to manage bots to report things to telegram.

"""

import datetime
import time
import warnings

import requests


class TelegramReporter:
    """Class to report to telegram

    This class is used to send messages to telegram via the telegram bot
    API. For regular usage, the `RunManager` and `TaskManager` classes
    use this class automatically, as long as configured correctly. For
    fine-grained control, this class can be used on its own.

    Parameters
    ----------
    bot_token
        The telegram bot token to use (this value should be a secret, so do not share it)
    chat_id
        The telegram chat ID the reporter should send messages to

    Attributes
    ----------
    bot_token
    chat_id

    Raises
    ------
    TypeError
        If a parameter has the incorrect type

    Examples
    --------
    >>> import lip_pps_run_manager as RM
    >>> bot = RM.TelegramReporter("SecretBotToken", "PostToThisChat_ID")

    """

    _bot_token = None
    _chat_id = None
    _session = None

    _last_message_time = datetime.datetime.now() - datetime.timedelta(seconds=5)
    _rate_limit = True  # If set, messages will be delayed to respect the rate limits set by telegram
    _rate_min_time = datetime.timedelta(seconds=1)  # Minimum allowed time between messages

    def __init__(self, bot_token: str, chat_id: str, rate_limit: bool = True):
        if not isinstance(bot_token, str):
            raise TypeError("The `bot_token` must be a str type object, received object of type {}".format(type(bot_token)))

        if not isinstance(chat_id, str):
            raise TypeError("The `chat_id` must be a str type object, received object of type {}".format(type(chat_id)))

        if not isinstance(rate_limit, bool):
            raise TypeError("The `rate_limit` must be a bool type object, received object of type {}".format(type(chat_id)))

        self._bot_token = bot_token
        self._chat_id = chat_id
        self._session = requests.Session()
        self._rate_limit = rate_limit

    def __repr__(self):
        """Get the python representation of this class"""
        return "TelegramReporter({}, {}, rate_limit={})".format(repr(self.bot_token), repr(self.chat_id), repr(self._rate_limit))

    @property
    def bot_token(self) -> str:
        """The token of the telegram bot property getter method"""
        return self._bot_token

    @property
    def chat_id(self) -> str:
        """The chat ID property getter method"""
        return self._chat_id

    def _send_message(self, message_text: str, reply_to_message_id: str = None):
        """Internal function to send a message to the chat using the bot.

        This is the internal counterpart to `send_message`. Avoid calling
        this function, since there are no checks on variable types or
        protections for exceptions. This function implements the base
        functionality of sending a message to telegram.

        Parameters
        ----------
        message_text
            The message the bot should send to the chat
        reply_to_message_id
            If the message is in reply to another message, place the ID
            of the message being replied to here

        """
        message_params = {'chat_id': self.chat_id, 'text': message_text}
        if reply_to_message_id is not None:
            message_params["reply_to_message_id"] = reply_to_message_id

        if self._rate_limit:
            if datetime.datetime.now() - self._last_message_time < self._rate_min_time:
                time.sleep((self._rate_min_time - (datetime.datetime.now() - self._last_message_time)).total_seconds())

        response = self._session.get(
            "https://api.telegram.org/bot{}/sendMessage".format(self.bot_token),
            data=message_params,
            timeout=1,
        )
        self._last_message_time = datetime.datetime.now()
        return response.json()

    def send_message(self, message_text: str, reply_to_message_id: str = None):
        """Send a message to the chat using the bot.

        Parameters
        ----------
        message_text
            The message the bot should send to the chat
        reply_to_message_id
            If the message is in reply to another message, place the ID
            of the message being replied to here

        Raises
        ------
        TypeError
            If a parameter has the wrong type
        Warning
            If any irregularity, leading to an exception occurs, it is reinterpreted as a warning

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> bot = RM.TelegramReporter("SecretBotToken", "PostToThisChat_ID")
        >>> bot.send_message("Hello World!")

        """
        if not isinstance(message_text, str):
            raise TypeError("The `message_text` must be a str type object, received object of type {}".format(type(message_text)))

        if reply_to_message_id is not None and not isinstance(reply_to_message_id, str):
            raise TypeError(
                "The `reply_to_message_id` must be a str type object, received object of type {}".format(type(reply_to_message_id))
            )

        try:
            return self._send_message(message_text, reply_to_message_id)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            warnings.warn("Failed sending to telegram. Reason: {}".format(repr(e)), category=RuntimeWarning)

    def _edit_message(self, message_text: str, message_id: str):
        """Internal function to edit a message that was previously sent to the chat using the bot.

        This is the internal counterpart to `edit_message`. Avoid calling
        this function, since there are no checks on variable types or
        protections for exceptions. This function implements the base
        functionality of editing a message on telegram.

        Parameters
        ----------
        message_text
            The message the bot should change to message to
        message_id
            The ID of the message to edit

        """
        if self._rate_limit:
            if datetime.datetime.now() - self._last_message_time < self._rate_min_time:
                time.sleep((self._rate_min_time - (datetime.datetime.now() - self._last_message_time)).total_seconds())

        response = self._session.post(
            "https://api.telegram.org/bot{}/editMessageText".format(self.bot_token),
            data={
                "chat_id": self.chat_id,
                "text": message_text,
                "message_id": message_id,
            },
            timeout=1,
        )

        self._last_message_time = datetime.datetime.now()
        return response.json()

    def edit_message(self, message_text: str, message_id: str):
        """Edit a message that was previously sent to the chat using the bot.

        Parameters
        ----------
        message_text
            The message the bot should change to message to
        message_id
            The ID of the message to edit

        Raises
        ------
        TypeError
            If a parameter has the wrong type
        Warning
            If any irregularity, leading to an exception occurs, it is reinterpreted as a warning

        Examples
        --------
        >>> import lip_pps_run_manager as RM
        >>> bot = RM.TelegramReporter("SecretBotToken", "PostToThisChat_ID")
        >>> bot.edit_message("New Message", "OldMessage_ID")

        """
        if not isinstance(message_text, str):
            raise TypeError("The `message_text` must be a str type object, received object of type {}".format(type(message_text)))

        if not isinstance(message_id, str):
            raise TypeError("The `message_id` must be a str type object, received object of type {}".format(type(message_id)))

        try:
            return self._edit_message(message_text, message_id)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            warnings.warn("Failed sending to telegram. Reason: {}".format(repr(e)), category=RuntimeWarning)
