from click.testing import CliRunner

from duple.duple import __version__
from duple.duple import cli
from duple.info import PYPROJECT


def test_version():
    truth_version = PYPROJECT["tool"]["poetry"]["version"]
    assert __version__ == truth_version

    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.output == f"duple version: {truth_version}\n"
