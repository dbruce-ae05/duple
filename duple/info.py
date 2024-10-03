import os
import sysconfig
from pathlib import Path
import tomllib

PROJECT_ROOT = Path(__file__).parent.parent
PROJECT_TOML = PROJECT_ROOT.joinpath("pyproject.toml")
USER_SCRIPTS_PATH = sysconfig.get_path("scripts", f"{os.name}_user")
VERSION_PATH = Path(__file__).parent.joinpath("__version__.py")
APP_NAME_PATH = Path(__file__).parent.joinpath("__app_name__.py")
LOGGING_CONFIGURATION_PATH = Path(__file__).parent.joinpath("logging_configuration.json")
LOGS_PATH = Path(__file__).parent.joinpath("logs")

if Path(PROJECT_TOML).exists():
    with PROJECT_TOML.open("rb") as toml_file:
        PYPROJECT = tomllib.load(toml_file)
