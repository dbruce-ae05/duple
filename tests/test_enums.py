from duple.status import Status
from duple.dispocode import DispoCode


def test_status():
    status = Status
    statuses = [value.name for value in Status]
    statuses.remove("POTENTIAL_DUPLICATE")
    statuses.remove("NOT_ANALYZED")

    stats = [len(value) for value in statuses]
    assert status.longest_status() == max(stats)


def test_dispocode():
    code = DispoCode
    codes = [value.name for value in DispoCode]
    stats = [len(value) for value in codes]
    assert code.longest_code() == max(stats)
