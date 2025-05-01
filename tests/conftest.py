import pytest
from pathlib import Path
import shutil


@pytest.fixture
def config_files(tmp_path):
    """Copy config files to temporary test directory"""
    test_config = tmp_path / "config"
    test_config.mkdir()

    # Copy your actual config files
    shutil.copy("config/default.yaml", test_config / "default.yaml")
    shutil.copy("config/prompts.yaml", test_config / "prompts.yaml")

    return str(test_config)