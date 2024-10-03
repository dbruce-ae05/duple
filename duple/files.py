from dataclasses import dataclass, field
from pathlib import Path
from duple.file import File
from duple.status import Status
from duple.dispocode import DispoCode
from tqdm.contrib.concurrent import process_map
from itertools import repeat
from duple.library import get_hash
from humanize import naturalsize
import os
from collections import Counter
from duple.decorators import log_func_time
from duple.app_logging import logger


"""
files is the collector the file class, files will:
-keep the all file objects up to date with the analysis results
-provide output file for duplicate review by user
-provide output of all files analyzed
-generate file objects from a list of paths (strings or Paths) and add to the collector
-identify duplicate/original files
    -preprocess on file size to reduce the number of hashes required
    -hash remainging files
    -identify original file based on input options
-ingest the output reviewed and updated by the user
-provide an iterable that cycles through all of the files and gives an action to take
"""


@dataclass
class Files(dict):
    duplicates: dict = field(init=False, default_factory=dict)
    test_functions: list = field(init=False, default_factory=list)
    max_workers: int = field(default=int(os.cpu_count() * 0.75) + 1)
    chunksize: int = field(default=2)
    hashalgo: str = field(default="sha256")
    duplicate_file_size: int = field(init=False, default=0)
    total_file_size: int = field(init=False, default=0)
    duplicate_file_count: int = field(init=False, default=0)
    duplicate_group_count: int = field(init=False, default=0)
    file_count: int = field(init=False, default=0)
    ignored_files: int = field(init=False, default=0)

    def _test_fun(self, attribute: str, minimum: bool, files: list[File]) -> list[File]:
        """
        test_fun returns a list of file objects that pass the test defined by attribute and minimum

        Args:
            attribute (str): attribute to test
            minimum (bool): true if attribute should be the minimum, false if the attribute should be the maxium
            files (list[File]): list of file objects to check

        Returns:
            list[File]: list of file objects that pass the test
        """

        temp = dict()
        for file in files:
            # print(file.__dict__)
            temp[str(file.path)] = file.__dict__[attribute]

        target = max(temp.items(), key=lambda x: x[1])
        if minimum:
            target = min(temp.items(), key=lambda x: x[1])

        target = temp[target[0]]

        return [file for file in files if file.__dict__[attribute] == target]

    @log_func_time
    def read_paths(self, paths: list):
        for path in paths:
            f = File(path)
            self[f.path] = f

    def get_paths(self) -> list:
        return list(self.keys())

    def get_status(self) -> dict:
        return {key: value.status for key, value in self.items()}

    @log_func_time
    def pre_process_files(self) -> None:
        """
        Eliminate files with unique sizes and ignored files, these can not be duplicates
        """
        sizes = dict()
        tempfile: File
        for tempfile in self.values():
            if tempfile.status == Status.IGNORED:
                continue

            if tempfile.size not in sizes.keys():
                sizes[tempfile.size] = list()

            sizes[tempfile.size].append(tempfile)

        itemlist: list
        for itemlist in sizes.values():
            item: File
            for item in itemlist:
                if len(itemlist) > 1:
                    self[item.path].status = Status.POTENTIAL_DUPLICATE
                else:
                    self[item.path].status = Status.IGNORED
                    self[item.path].dispocode = DispoCode.UNIQUE_FILE_SIZE

    @log_func_time
    def process_files(self) -> None:
        logger.debug("ID of Potential Duplicates START")
        potential_duplicates = list()
        tempfile: File
        for tempfile in self.values():
            if tempfile.status == Status.POTENTIAL_DUPLICATE:
                potential_duplicates.append(str(tempfile.path))
        logger.debug("ID of Potential Duplicates FINISH")

        logger.debug("Hashing Files START")
        hashes = process_map(
            get_hash,
            potential_duplicates,
            repeat(self.hashalgo),
            max_workers=self.max_workers,
            chunksize=self.chunksize,
            desc="hashing files",
        )
        logger.debug("Hashing Files FINISH")

        logger.debug("Recording Hash Values to Files START")
        for hash, path in hashes:
            if not hash:
                self[Path(path)].status = Status.IGNORED
                self[Path(path)].dispocode = DispoCode.PERMISSION_DENIED
            else:
                self[Path(path)].hash = hash
        logger.debug("Recording Hash Values to Files FINISH")

        logger.debug("Making Duplicates List START")
        for value in self.values():
            if value.hash not in self.duplicates.keys() and value.status == Status.POTENTIAL_DUPLICATE:
                self.duplicates[value.hash] = list()
            if value.status == Status.POTENTIAL_DUPLICATE:
                self.duplicates[value.hash].append(value)
        logger.debug("Making Duplicates List FINISH")

        logger.debug("Marking Ignored/Duplicate START")
        for items in self.duplicates.values():
            for item in items:
                self[item.path].twins = len(items) - 1  # [tfile.path for tfile in items if tfile != item]
                if len(items) == 1:
                    self[item.path].status = Status.IGNORED
                    self[item.path].dispocode = DispoCode.UNIQUE_HASH
                if len(items) > 1:
                    self[item.path].status = Status.DUPLICATE
        logger.debug("Marking Ignored/Duplicate FINISH")

        logger.debug("Finalizing Duplicates START")
        self.duplicates = {key: value for key, value in self.duplicates.items() if len(value) > 1}
        logger.debug("Finalizing Duplicates FINISH")

    @log_func_time
    def determine_originals(self, options: list):
        """
        options = tuple(attribute: str, minimum: bool)
        """
        if not isinstance(options, list):
            raise Exception(TypeError, f"options must be type = list, provided type = {type(options)}")

        for option in options:
            if not isinstance(option, tuple):
                raise Exception(TypeError, f"options must be a list of tuples, provided a list of {type(option)}")

            if option[0] not in File.get_available_option_attributes():
                raise Exception(
                    ValueError, f"first item in tuple must be in the list {File.get_available_option_attributes()}"
                )

            if option[1] not in [True, False]:
                raise Exception(ValueError, "second item in tuple must be True or False")

        for twins in self.duplicates.values():
            result = twins  # deepcopy(twins)

            for attribute, minimum in options:
                result = self._test_fun(attribute, minimum, result)

            original = result[0]
            self[original.path].status = Status.ORIGINAL

            for item in twins:
                if item.path != original.path:
                    self[item.path].status = Status.DUPLICATE

        self.calculate_totals()

    @log_func_time
    def create_duplicate_output(self) -> list:
        lines = list()
        for twins in self.duplicates.values():
            for file in twins:
                line = f"{str(file.status.name).ljust(Status.longest_status() + 2)}|"
                line += f"{naturalsize(file.size).center(13)}|"
                line += f" {file.path}"
                lines.append(line)
            lines.append("")

        return lines

    @log_func_time
    def create_ignored_files_output(self) -> list:
        lines = list()
        file: File
        logger.debug("Called Create Ignored Files Output")
        for file in self.values():
            if file.status.name == Status.IGNORED.name:
                line = f"{str(file.status.name).ljust(Status.longest_status() + 2)}|"
                line += f"{naturalsize(file.size).center(13)}|"
                line += f"{str(file.dispocode.name).center(DispoCode.longest_code() + 3)}|"
                line += f" {file.path}"
                lines.append(line)
        return lines

    def perform_analysis(self) -> None:
        self.pre_process_files()
        self.process_files()

    @log_func_time
    def calculate_totals(self):
        c = Counter([file.status for file in self.values()])

        self.duplicate_group_count = len(self.duplicates.keys())
        self.file_count = len(self.keys())
        self.duplicate_file_count = c[Status.DUPLICATE]
        self.ignored_files = c[Status.IGNORED]

        for file in self.values():
            if file.status == Status.DUPLICATE:
                self.duplicate_file_size += file.size
            self.total_file_size += file.size
