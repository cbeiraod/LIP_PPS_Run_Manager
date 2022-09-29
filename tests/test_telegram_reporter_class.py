import lip_pps_run_manager as RM


class SessionReplacement:
    _params = {}
    _error_type = None

    def __init__(self, error_type=None):
        self._error_type = error_type
        pass

    def get(self, url: str, data=None, timeout=None):
        if self._error_type is not None:
            if self._error_type == "KeyboardInterrupt":
                raise KeyboardInterrupt
            elif self._error_type == "Exception":  # pragma: no cover
                raise Exception()
        self._params = {}

        self._params["url"] = url
        self._params["data"] = data
        self._params["timeout"] = timeout
        return self

    def json(self):
        return self._params


def test_telegram_reporter():
    reporter = RM.TelegramReporter("bot_token", "chat_id")

    assert reporter.bot_token == "bot_token"
    assert reporter.chat_id == "chat_id"


def test_fail_telegram_reporter():
    try:
        RM.TelegramReporter(1, "chat_id")
    except TypeError as e:
        assert str(e) == ("The `bot_token` must be a str type object, received object of type <class 'int'>")

    try:
        RM.TelegramReporter("bot_token", 1)
    except TypeError as e:
        assert str(e) == ("The `chat_id` must be a str type object, received object of type <class 'int'>")


def test_telegram_reporter_send_message():
    sessionHandler = SessionReplacement()
    bot_token = "bot_token"
    chat_id = "chat_id"
    reporter = RM.TelegramReporter(bot_token, chat_id)
    reporter._session = sessionHandler  # This prevents actual HTTP requests from being generated

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


def test_fail_telegram_reporter_send_message():
    sessionHandler = SessionReplacement(error_type="KeyboardInterrupt")
    sessionHandler2 = SessionReplacement(error_type="Exception")
    bot_token = "bot_token"
    chat_id = "chat_id"
    reporter = RM.TelegramReporter(bot_token, chat_id)
    reporter._session = sessionHandler  # This prevents actual HTTP requests from being generated

    message = "Hello there"

    try:
        reporter.send_message(message_text=1, reply_to_message_id=None)
    except TypeError as e:
        assert str(e) == ("The `message_text` must be a str type object, received object of type <class 'int'>")

    try:
        reporter.send_message(message_text=message, reply_to_message_id=1)
    except TypeError as e:
        assert str(e) == ("The `reply_to_message_id` must be a str type object, received object of type <class 'int'>")

    try:
        reporter.send_message(message_text=message, reply_to_message_id=None)
    except KeyboardInterrupt as e:
        assert isinstance(e, KeyboardInterrupt)

    reporter._session = sessionHandler2
    try:
        reporter.send_message(message_text=message, reply_to_message_id=None)
    except RuntimeWarning as e:
        assert str(e) == "Failed sending to telegram. Reason: Exception()"
