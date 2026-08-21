from pathlib import Path

from shipcheck.config import CONFIG_FILE, create_default_config, load_config


def test_create_and_load_config(tmp_path: Path) -> None:
    path = create_default_config(tmp_path)

    assert path.name == CONFIG_FILE
    config = load_config(tmp_path)
    assert config.release_branch == "main"
    assert config.default_bump == "patch"
