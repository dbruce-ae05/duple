from enum import Enum, auto


class DispoCode(Enum):
    UNIQUE_FILE_SIZE = auto()
    UNIQUE_HASH = auto()
    PERMISSION_DENIED = auto()
    NOT_SET = auto()

    def longest_code():
        codes = [value.name for value in DispoCode]

        result = max([len(str(value)) for value in codes])
        return result
