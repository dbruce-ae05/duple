from duple.file import File
from pathlib import Path
import hashlib
from duple.library import get_available_hashes


def test_file():
    tf = Path(__file__)
    f: File = File(__file__)
    assert tf == f.path

    f = File(Path(__file__))
    assert tf == f.path

    assert tf.stat().st_size == f.size
    assert tf.stat().st_atime == f.atime
    assert tf.stat().st_mtime == f.mtime
    assert tf.stat().st_ctime == f.ctime
    assert len(tf.parents) == f.depth

    for hash in get_available_hashes():
        with open(tf, "rb") as temp:
            digest = hashlib.file_digest(temp, hash)

        assert digest.hexdigest() == f.calc_hash(hash).hash
