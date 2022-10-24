import shutil
import tempfile
from pathlib import Path

import lip_pps_run_manager.run_manager as internalRM


def test_run_exists_function():
    tmpdir = tempfile.gettempdir()
    runName = "hopefully_unique_run_name"
    p = Path(tmpdir) / runName
    p.mkdir(exist_ok=True)
    (p / 'run_info.txt').touch()
    assert internalRM.run_exists(Path(tmpdir), runName)  # Test when exists
    shutil.rmtree(p)
    assert not internalRM.run_exists(Path(tmpdir), runName)  # Test when doesn't exist


def test_fail_run_exists_function():
    try:
        internalRM.run_exists(".", "a")
    except TypeError as e:
        assert str(e) == ("The `path_to_directory` must be a Path type object, received object of type <class 'str'>")

    try:
        internalRM.run_exists(Path("."), 2)
    except TypeError as e:
        assert str(e) == ("The `run_name` must be a str type object, received object of type <class 'int'>")


def test_clean_path_function():
    assert isinstance(internalRM.clean_path(Path(".")), Path)  # Test return type
    # TODO: assert RM.clean_path(Path("./Run@2")) == Path("./Run2") # Test actual cleaning


def test_fail_clean_path_function():
    try:
        internalRM.clean_path(".")
    except TypeError as e:
        assert str(e) == ("The `path_to_clean` must be a Path type object, received object of type <class 'str'>")


def test_create_run_function():
    tmpdir = tempfile.gettempdir()
    basePath = Path(tmpdir)
    runName = "testRun_21"

    assert internalRM.create_run(basePath, runName) == basePath / runName
    assert (basePath / runName).is_dir()
    assert (basePath / runName / "run_info.txt").is_file()
    # TODO: Check contents of run_info.txt file
    shutil.rmtree(basePath / runName)
    assert not (basePath / runName).is_dir()


def test_fail_create_run_function():
    tmpdir = tempfile.gettempdir()
    basePath = Path(tmpdir)
    runName = "testRun_21"

    try:
        internalRM.create_run(".", runName)
    except TypeError as e:
        assert str(e) == ("The `path_to_directory` must be a Path type object, received object of type <class 'str'>")

    try:
        internalRM.create_run(basePath, 2)
    except TypeError as e:
        assert str(e) == ("The `run_name` must be a str type object, received object of type <class 'int'>")

    try:
        internalRM.create_run(basePath, runName)
        internalRM.create_run(basePath, runName)
    except RuntimeError as e:
        shutil.rmtree(basePath / runName)
        assert str(e) == (
            "Unable to create the run '{}' in '{}' because a directory with that name already exists.".format(runName, str(basePath))
        )


def test_load_telegram_config_function():
    config_file = Path.cwd() / "run_manager_telegram_config.json"
    with config_file.open("w", encoding="utf-8") as file:
        file.write("{\n")
        file.write('  "bots": {\n')
        file.write('    "testBot": "bot_token"\n')
        file.write("  },\n")
        file.write('  "chats": {\n')
        file.write('    "testChat": "chat_id"\n')
        file.write("  }\n")
        file.write("}\n")

        file.close()

    cfg = internalRM.load_telegram_config()

    assert "bots" in cfg
    assert "testBot" in cfg["bots"]
    assert cfg["bots"]["testBot"] == "bot_token"
    assert "chats" in cfg
    assert "testChat" in cfg["chats"]
    assert cfg["chats"]["testChat"] == "chat_id"

    config_file.unlink()
