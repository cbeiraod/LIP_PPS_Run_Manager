import lip_pps_run_manager as RM


class SessionReplacement:
    def __init__(self):
        2


def test_telegram_reporter():
    reporter = RM.TelegramReporter("bot_token", "chat_id")

    assert reporter.bot_token == "bot_token"
    assert reporter.chat_id == "chat_id"
