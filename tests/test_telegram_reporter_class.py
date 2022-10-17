from unittest.mock import patch

import lip_pps_run_manager as RM


class SessionReplacement:
    _params = {}
    _prev_params = {}
    _error_type = None

    def __init__(self):
        pass

    def __getitem__(self, key: str):
        if key == 'result':
            return {'message_id': "This is the message ID"}
        if key == 'previous message':
            return self._prev_params
        if key in self._params:
            return self._params[key]
        raise RuntimeError("Unknown key: {}".format(key))  # pragma: no cover

    def _set_error_type(self, error_type=None):
        self._error_type = error_type

    def _clear(self):
        self._params = {}
        self._prev_params = {}

    def get(self, url: str, data=None, timeout=None):
        if self._params != {}:
            self._prev_params = self._params
        self._params = {}

        self._params["url"] = url
        self._params["data"] = data
        self._params["timeout"] = timeout

        if self._error_type is not None:
            if self._error_type == "KeyboardInterrupt":
                raise KeyboardInterrupt
            elif self._error_type == "Exception":  # pragma: no cover
                raise Exception()

        return self

    def post(self, url: str, data=None, timeout=None):
        if self._params != {}:
            self._prev_params = self._params
        self._params = {}

        self._params["url"] = url
        self._params["data"] = data
        self._params["timeout"] = timeout

        if self._error_type is not None:
            if self._error_type == "KeyboardInterrupt":
                raise KeyboardInterrupt
            elif self._error_type == "Exception":  # pragma: no cover
                raise Exception()

        return self

    def json(self):
        return self


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_telegram_reporter():
    reporter = RM.TelegramReporter("bot_token", "chat_id")

    assert reporter.bot_token == "bot_token"
    assert reporter.chat_id == "chat_id"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_fail_telegram_reporter():
    try:
        RM.TelegramReporter(1, "chat_id")
    except TypeError as e:
        assert str(e) == ("The `bot_token` must be a str type object, received object of type <class 'int'>")

    try:
        RM.TelegramReporter("bot_token", 1)
    except TypeError as e:
        assert str(e) == ("The `chat_id` must be a str type object, received object of type <class 'int'>")


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_telegram_reporter_send_message():
    bot_token = "bot_token"
    chat_id = "chat_id"
    reporter = RM.TelegramReporter(bot_token, chat_id, rate_limit=False)
    sessionHandler = reporter._session

    message = "Hello there"
    retVal = reporter.send_message(message_text=message, reply_to_message_id=None)

    assert retVal == sessionHandler.json()
    assert retVal["timeout"] == 1
    assert retVal["url"] == "https://api.telegram.org/bot{}/sendMessage".format(bot_token)
    assert "reply_to_message_id" not in retVal["data"]
    assert retVal["data"]['chat_id'] == chat_id
    assert retVal["data"]['text'] == message

    reply_to_message_id = "123"
    retVal = reporter.send_message(message_text=message, reply_to_message_id=reply_to_message_id)

    assert retVal == sessionHandler.json()
    assert retVal["data"]["reply_to_message_id"] == reply_to_message_id


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_fail_telegram_reporter_send_message():
    bot_token = "bot_token"
    chat_id = "chat_id"
    reporter = RM.TelegramReporter(bot_token, chat_id, rate_limit=False)
    sessionHandler = reporter._session

    message = "Hello there"

    try:
        reporter.send_message(message_text=1, reply_to_message_id=None)
    except TypeError as e:
        assert str(e) == ("The `message_text` must be a str type object, received object of type <class 'int'>")

    try:
        reporter.send_message(message_text=message, reply_to_message_id=1)
    except TypeError as e:
        assert str(e) == ("The `reply_to_message_id` must be a str type object, received object of type <class 'int'>")

    sessionHandler._set_error_type(error_type="KeyboardInterrupt")
    try:
        reporter.send_message(message_text=message, reply_to_message_id=None)
    except KeyboardInterrupt as e:
        assert isinstance(e, KeyboardInterrupt)

    sessionHandler._set_error_type(error_type="Exception")
    try:
        reporter.send_message(message_text=message, reply_to_message_id=None)
    except RuntimeWarning as e:
        assert str(e) == "Failed sending to telegram. Reason: Exception()"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_telegram_reporter_edit_message():
    bot_token = "bot_token"
    chat_id = "chat_id"
    reporter = RM.TelegramReporter(bot_token, chat_id, rate_limit=False)
    sessionHandler = reporter._session

    message = "Hello there"
    message_id = "message_id"
    retVal = reporter.edit_message(message_text=message, message_id=message_id)

    assert retVal == sessionHandler.json()
    assert retVal["timeout"] == 1
    assert retVal["url"] == "https://api.telegram.org/bot{}/editMessageText".format(bot_token)
    assert retVal["data"]["message_id"] == message_id
    assert retVal["data"]['chat_id'] == chat_id
    assert retVal["data"]['text'] == message


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_fail_telegram_reporter_edit_message():
    bot_token = "bot_token"
    chat_id = "chat_id"
    reporter = RM.TelegramReporter(bot_token, chat_id, rate_limit=False)
    sessionHandler = reporter._session

    message = "Hello there"
    message_id = "message_id"

    try:
        reporter.edit_message(message_text=1, message_id=message_id)
    except TypeError as e:
        assert str(e) == ("The `message_text` must be a str type object, received object of type <class 'int'>")

    try:
        reporter.edit_message(message_text=message, message_id=1)
    except TypeError as e:
        assert str(e) == ("The `message_id` must be a str type object, received object of type <class 'int'>")

    sessionHandler._set_error_type(error_type="KeyboardInterrupt")
    try:
        reporter.edit_message(message_text=message, message_id=message_id)
    except KeyboardInterrupt as e:
        assert isinstance(e, KeyboardInterrupt)

    sessionHandler._set_error_type(error_type="Exception")
    try:
        reporter.edit_message(message_text=message, message_id=message_id)
    except RuntimeWarning as e:
        assert str(e) == "Failed sending to telegram. Reason: Exception()"


@patch('requests.Session', new=SessionReplacement)  # To avoid sending actual http requests
def test_telegram_reporter_repr():
    bot_token = "bot_token"
    chat_id = "chat_id"
    rate_limit = False
    reporter = RM.TelegramReporter(bot_token, chat_id, rate_limit=rate_limit)

    assert repr(reporter) == "TelegramReporter({}, {}, rate_limit={})".format(repr(bot_token), repr(chat_id), repr(rate_limit))
