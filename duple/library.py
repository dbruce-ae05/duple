import hashlib
from pathlib import Path
import os
from time import perf_counter
from tqdm import tqdm
from random import choice, choices, randint
from string import ascii_letters
from send2trash import send2trash
import json
from datetime import datetime as dt, timezone
import click
from duple.decorators import log_func_time, log_func_with_args
from duple.info import LOGS_PATH

from typing import Iterator
from time import sleep


def get_latest_file(inpath: str, filter: str = None, recurse: bool = False) -> str:
    files = list()

    path: Path
    path = inpath
    if isinstance(path, str):
        path = Path(path)

    def add_file(file: Path):
        if file.is_file() and (filter is None or filter in file.name):
            files.append(file)

    if recurse:
        for r, fd, fs in os.walk(path):
            for f in fs:
                file: Path = Path(r).joinpath(f)
                add_file(file)
    else:
        for f in os.listdir(path):
            file = Path(path).joinpath(f)
            add_file(file)

    if files is None:
        raise Exception(FileNotFoundError)

    atimes = {str(path.absolute()): path.stat().st_atime for path in files}
    min_file = max(atimes.items(), key=lambda x: x[1])

    # logger.info(f'latest accessed file: {min_file[0]}')
    return min_file[0]


def follow_log(level: str = "DEBUG", filter: str = None):
    level = level.upper()
    levels = {
        "NOTSET": {"color": "white", "value": 0},
        "DEBUG": {"color": "green", "value": 10},
        "INFO": {"color": "magenta", "value": 20},
        "WARNING": {"color": "yellow", "value": 30},
        "ERROR": {"color": "bright_red", "value": 40},
        "CRITICAL": {"color": "bright_red", "value": 50},
    }

    file_path = get_latest_file(LOGS_PATH, filter=".jsonl")
    # logger.debug(f'Latest log file is {file_path}')
    try:
        with open(file_path, "r") as file:
            line = file.readline()
            print(line)

            for line in follow(file):
                parsed = json.loads(line)
                style_ts = click.style(f"[{parsed['timestamp']}]", fg="cyan")
                style_level = click.style(f"[{parsed['level']}]", fg=levels[parsed["level"]]["color"])
                style_module = click.style(parsed["module"], fg="white")
                style_function = click.style(parsed["function"], fg="white")
                style_message = click.style(parsed["message"], fg=levels[parsed["level"]]["color"])
                style_msg_pointer = click.style("->", fg="bright_blue")

                if levels[parsed["level"]]["value"] >= levels[level]["value"] and (filter is None or filter in line):
                    click.secho(
                        f"{style_ts} {style_level} {style_module}.{style_function} {style_msg_pointer} {style_message}"
                    )

                # if Path(file_path).is_file():
                #     new_file_path = get_latest_file(LOGS_PATH, filter = '.jsonl')
                #     if file_path != new_file_path:
                #         #logger.debug(f'Log file rollover detected, switching to newest log: {file_path}')
                #         file_path = new_file_path
    except:  # noqa E722
        pass


def follow(file, sleep_sec=0.1) -> Iterator[str]:
    """Yield each line from a file as they are written.
    `sleep_sec` is the time to sleep after empty reads."""
    line: str = str()
    while True:
        tmp = file.readline()
        if tmp is not None and tmp != "":
            line += tmp
            if line.endswith("\n"):
                yield line
                line = ""
        elif sleep_sec:
            sleep(sleep_sec)


def dump_dict_to_json(input: dict, filename: str, indent: int = 4):
    with open(filename, "w") as f:
        json.dump(input, f, indent=indent)


def get_available_hashes() -> list:
    hashes = list(hashlib.algorithms_available)
    hashes.remove("shake_128")
    hashes.remove("shake_256")
    hashes.sort()
    return hashes


@log_func_with_args
def gen_test_files(test_path_root: Path, numdirs: int, numfiles: int, max_file_size: int):
    if not Path(test_path_root).exists():
        os.mkdir(test_path_root)

    file_sizes = [x for x in range(max_file_size)]
    # data = [os.urandom(file_size) for _ in range(int(numfiles/2))]
    data = [os.urandom(choice(file_sizes)) for _ in range(int((numfiles * numdirs) / 2))]

    for i in tqdm(range(numdirs), desc="making directories", position=0):
        dir_path = test_path_root.joinpath("".join(choices(ascii_letters, k=randint(3, 30))))
        dir_path2 = dir_path.joinpath("".join(choices(ascii_letters, k=randint(3, 30))))

        if not Path(dir_path).exists():
            os.mkdir(dir_path)

        if not Path(dir_path2).exists():
            os.mkdir(dir_path2)

        for j in range(numfiles):
            file_name = "".join(choices(ascii_letters, k=randint(3, 30)))
            file_path = Path(choice([dir_path, dir_path2])).joinpath(file_name + ".txt")

            if file_path.exists():
                continue

            with open(file_path, "wb") as f:
                f.write(choice(data))


def get_hash(path: str, hash: str) -> str | str:
    try:
        with open(path, "rb") as f:
            digest = hashlib.file_digest(f, hash)
        return digest.hexdigest(), path
    except PermissionError:
        return "", path


@log_func_with_args
def timed_get_hash(hash: str, path: str) -> float:
    start = perf_counter()
    get_hash(path, hash)
    finish = perf_counter()
    return hash, finish - start


def get_max_workers():
    return int(os.cpu_count() * 0.75) + 1


def tree(dir_path: Path, prefix: str = ""):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """

    # prefix components:
    space = "    "
    branch = "│   "
    # pointers:
    tee = "├── "
    last = "└── "

    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield [prefix, pointer, path.name, path.is_dir()]
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)


def generate_options_list(flags: list) -> list[tuple]:
    options = list()
    if flags[0]:
        option = ("depth", True)
        options.append(option)
    if flags[1]:
        option = ("depth", False)
        options.append(option)
    if flags[2]:
        option = ("namelength", True)
        options.append(option)
    if flags[3]:
        option = ("namelength", False)
        options.append(option)
    if flags[4]:
        option = ("atime", True)
        options.append(option)
    if flags[5]:
        option = ("atime", False)
        options.append(option)
    if flags[6]:
        option = ("ctime", True)
        options.append(option)
    if flags[7]:
        option = ("ctime", False)
        options.append(option)
    if flags[8]:
        option = ("mtime", True)
        options.append(option)
    if flags[9]:
        option = ("mtime", False)
        options.append(option)

    return options


@log_func_with_args
def remove_empty_directories(path: str, verbose: bool = False) -> None:
    for root, folders, files in tqdm(
        os.walk(path), desc="Removing .DS_Store files from empty directories", leave=False
    ):
        if ".DS_Store" in files and len(files) == 1:
            temp_path = str(Path(root).joinpath(".DS_Store").absolute())
            send2trash(temp_path)

    dirs = list()
    for root, folders, files in os.walk(os.getcwd()):
        if not files and not folders:
            dirs.append(root)

    dirs = sorted(dirs, key=lambda x: -1 * len(Path(x).parents))

    if len(dirs) == 0:
        return

    # [ 100.0%] deleted             90 Bytes  nZp/enRmIFgQjR/iZSR.txt

    if verbose:
        cnt = 0
        for dir in dirs:
            cnt += 1
            completestyle = click.style(f"[{cnt / len(dirs) * 100: 6.1f}%]", fg="cyan")
            deldirstyle = click.style("deleting empty directory: ", fg="yellow")
            click.secho(f"{completestyle} {deldirstyle} {dir}")
            send2trash(dir)
    else:
        for dir in tqdm(dirs, desc="Removing empty directories"):
            send2trash(dir)


@log_func_time
def create_output(inputs: list, output_dir: str, dupes: list, ignored_files: list, summary_statistics: dict) -> None:
    max_len_key = max([len(k) for k in summary_statistics.keys()])
    max_len_val = max([len(str(v)) for v in summary_statistics.values()])

    section_divider = f"\n{''.rjust(max_len_key + max_len_val + 10,'-')}\n"

    # output_json = Path(output_dir).joinpath('duple.json')
    output_delete = Path(output_dir).joinpath("duple.delete")

    for key, value in summary_statistics.items():
        if "(seconds)" in key:
            summary_statistics[key] = f"{round(value, 5):.5f}"
            value = summary_statistics[key]

        click.secho(
            f'{key.ljust(max_len_key + max_len_val - len(str(value)) + 10, ".")}{click.style(str(value), fg = "green")}'
        )

    click.secho()
    click.secho(
        "Open the `output summary results` file listed above with a text editor for review",
        fg="yellow",
    )
    click.secho("Once review and changes are complete, run `duple rm`", fg="yellow")

    # dump_dict_to_json(all_files, output_json.absolute())

    with open(output_delete, "w", encoding="utf-8") as f:
        f.write(
            f"Duple Report Generated on {dt.now(timezone.utc).astimezone().isoformat()}, commanded by user: {os.getlogin()}"
        )
        f.write(section_divider)
        f.write("Summary Statistics:\n")
        for key, value in summary_statistics.items():
            f.write(f'{key.ljust(max_len_key + max_len_val - len(str(value)) + 10,".")}{str(value)}\n')
        f.write(section_divider)
        f.write("Inputs (True = minimum, False = Maximum): \n")
        for input in inputs:
            f.write(f"{input[0]} = {input[1]}\n")

        f.write(section_divider)
        f.write("Outputs:\n")
        # f.write(f"{str(output_json.absolute())}\n")
        f.write(f"{str(output_delete.absolute())}\n")

        f.write(section_divider)
        f.write("Instructions to User:\n")
        f.write(
            "The sections below describe what action duple will take when 'duple rm' is commanded."
            " The first column is the flag that tells duple what to do:\n"
            "\tORIGINAL   : means duple will take no action for this file, listed only as a reference to the user\n"
            "\tDUPLICATE  : means duple will send this file to the trash can or recycling bin, if able\n"
        )

        f.write(section_divider)
        f.write("Duplicate Results:\n")
        if len(dupes) == 0:
            f.write("No duplicates found.\n")

        for line in dupes:
            f.write(f"{line}\n")

        f.write(section_divider)
        f.write("Ignored Files in Scan:\n")
        for line in ignored_files:
            f.write(f"{line}\n")


@log_func_with_args
def get_delete_paths(path: Path) -> dict:
    if not duple_outputs_exist(path):
        return

    with open(path.joinpath("duple.delete"), "r") as f:
        items = f.read().splitlines()

    results = dict()
    flag = False
    for item in items:
        if item == "Duplicate Results:":
            flag = True

        if flag and "----" in item:
            break

        if flag and item.split("|")[0].strip() in ["DUPLICATE", "ORIGINAL"]:
            item_split = item.split("|")
            action = item_split[0].strip()
            size = item_split[1]  # .strip()
            path = item_split[2][1:].strip()
            results[path] = {"type": action, "size": size, "path": path}

    return results


def duple_outputs_exist(path: Path) -> bool:
    if not path.joinpath("duple.delete").exists():
        click.secho("duple.delete do no exists - run duple scan to create this file")
        return False
    return True


def delete_logs() -> str:
    files = os.listdir(LOGS_PATH)
    for file in files:
        p = Path(LOGS_PATH).joinpath(file)
        p.unlink()

    p = Path(LOGS_PATH).joinpath("log.jsonl")
    with open(p, "a"):
        pass

    p = p.parent.joinpath("log.log")
    with open(p, "a"):
        pass

    return f"Deleted Log Files: {files}"
