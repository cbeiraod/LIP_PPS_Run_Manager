import lip_pps_run_manager as RM


class SessionReplacement:
    def __init__(self):
        2


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
