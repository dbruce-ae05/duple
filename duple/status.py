from enum import Enum, auto


class Status(Enum):
    IGNORED = auto()
    POTENTIAL_DUPLICATE = auto()
    DUPLICATE = auto()
    ORIGINAL = auto()
    NOT_ANALYZED = auto()

    def longest_status():
        statuses = [value.name for value in Status]
        statuses.remove("POTENTIAL_DUPLICATE")
        statuses.remove("NOT_ANALYZED")

        result = max([len(str(value)) for value in statuses])
        return result
