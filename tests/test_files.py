from duple.files import Files
from duple.file import File
from pathlib import Path
import os
from duple.status import Status
from collections import Counter
from copy import deepcopy

files: Files = Files()


def test_files(create_test_files):
    filelist = list()
    for r, fds, fs in os.walk(create_test_files, followlinks=False):
        for f in fs:
            filelist.append(Path(r).joinpath(f))

    files.read_paths(filelist)
    assert filelist == files.get_paths()

    status_dict = {path: Status.NOT_ANALYZED for path in filelist}
    assert status_dict == files.get_status()

    files.pre_process_files()
    assert status_dict != files.get_status()

    status_dict = files.get_status()
    for value in status_dict.values():
        assert value != Status.NOT_ANALYZED

    files.process_files()

    file: File
    for file in files.values():
        assert file.status != Status.POTENTIAL_DUPLICATE


def test_files_originals_single_attributes():
    new_files = deepcopy(files)

    options = list()
    for attribute in File.get_available_option_attributes():
        for i in range(2):
            option = [(attribute, i == 0)]
            options.append(option)

    for option in options:
        new_files = deepcopy(files)
        new_files.determine_originals((option))

        for twins in new_files.duplicates.values():
            twinstatus = [file.status for file in twins]
            counts = Counter(twinstatus)
            assert counts[Status.ORIGINAL] == 1

            if option[0][1]:
                target = min([file.__dict__[option[0][0]] for file in twins])
            else:
                target = max([file.__dict__[option[0][0]] for file in twins])

            for file in twins:
                if file.status == Status.ORIGINAL:
                    assert target == file.__dict__[option[0][0]]


def test_files_duplicates_same_size():
    file: File
    sizes: set
    for twins in files.duplicates.values():
        sizes = set()
        for file in twins:
            sizes.add(file.size)
        assert len(sizes) == 1


def test_files_create_duplicate_output():
    new_files = deepcopy(files)

    options = [("depth", True), ("namelength", True)]
    new_files.determine_originals(options)
    lines = new_files.create_duplicate_output()
    print()
    for line in lines:
        print(line)


def test_files_create_ignored_files_output():
    new_files = deepcopy(files)

    options = [("depth", True), ("namelength", True)]
    new_files.determine_originals(options)
    lines = new_files.create_ignored_files_output()
    print()
    for line in lines:
        print(line)
