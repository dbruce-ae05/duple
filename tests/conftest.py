import pytest  # type: ignore
from duple.info import PROJECT_ROOT
from duple.library import gen_test_files


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def create_test_files(tmp_path_factory):
    temp_path = tmp_path_factory.mktemp("temp_files")
    gen_test_files(temp_path, 20, 100, 4096)
    return temp_path
