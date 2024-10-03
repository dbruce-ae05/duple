from pathlib import Path
from duple.library import get_latest_file


def test_library_get_latest_file(create_test_files):
    new_file = str(Path(create_test_files).joinpath("newest_file.txt").absolute())

    with open(new_file, "w") as f:
        f.write("new file")
    print(get_latest_file(create_test_files))
    assert new_file == get_latest_file(create_test_files)

    with open(new_file, "w") as f:
        f.write("new file")
    print(get_latest_file(create_test_files, recurse=True))
    assert new_file == get_latest_file(create_test_files, recurse=True)
