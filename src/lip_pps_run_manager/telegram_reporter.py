# -*- coding: utf-8 -*-
"""The Telegram Reporter module

Contains classes and functions used to manage bots to report things to telegram.

"""

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

        response = self._session.get(
            "https://api.telegram.org/bot{}/sendMessage".format(self.bot_token),
            data=message_params,
            timeout=1,
        )
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
            return self._send_message(str(message_text), reply_to_message_id)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            warnings.warn("Failed sending to telegram. Reason: {}".format(repr(e)), category=RuntimeWarning)
