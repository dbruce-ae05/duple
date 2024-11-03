import os
import subprocess
import sys
from itertools import repeat
from pathlib import Path
from statistics import mean, median, mode, stdev
from time import perf_counter

import click
from tqdm.contrib.concurrent import process_map, thread_map

from duple.library import get_hash


@click.group()
def perf_test():
    pass


def describe(data: list, decimals: int):
    stats = [mean, median, mode, stdev]

    result = list()
    for stat in stats:
        result.append(f"{stat.__name__} = {round(stat(data), decimals)}")

    return ", ".join(result)


def traversal_os_walk(path: Path) -> int:
    start = perf_counter()
    cnt = 0
    for r, ds, fs in os.walk(path):
        for f in fs:
            if Path(r).joinpath(f).exists:
                cnt += 1
    finish = perf_counter()
    return finish - start, cnt


def traversal_find_cmd(path: Path) -> int:
    start = perf_counter()
    cnt = 0
    result = subprocess.run(f'find "{str(path.absolute())}" -type f', stdout=subprocess.PIPE, shell=True)
    files = result.stdout.decode("utf-8").splitlines()
    for file in files:
        if Path(file).exists():
            cnt += 1
    finish = perf_counter()
    return finish - start, cnt


@perf_test.command()
@click.option("--path", "-p", type=click.Path())
@click.option("--trials", "-t", type=click.INT, default=2)
def test_traversals(path: Path, trials: int) -> None:
    funcs = [traversal_os_walk, traversal_find_cmd]
    max_fun_nam = max([len(fun.__name__) for fun in funcs])
    path = Path(path)
    stats = dict()

    for _ in range(trials):
        for fun in funcs:
            if fun.__name__ not in stats.keys():
                stats[fun.__name__] = list()
            result = fun(path)
            stats[fun.__name__].append(result[0])

    for func, result in stats.items():
        print(f"{func.ljust(max_fun_nam)} was run for {trials=}, stats: {describe(result, 5)} seconds")


@perf_test.command()
@click.option("--compose-file", help="compose file to work with", type=click.File("r"), default=sys.stdin)
def test_stdin(compose_file: click.File) -> str:
    start = perf_counter()
    with compose_file:
        output = compose_file.read()
    lines = output.split("\n")

    for line in lines:
        path = Path(line)
        print(path)

    print()
    print(f"Elapsed time: {round(perf_counter() - start,4)}")


def get_files(path: Path) -> list:
    files: list = list()
    for r, ds, fs in os.walk(path):
        for f in fs:
            if Path(r).joinpath(f).exists:
                files.append(Path(r).joinpath(f))
    return files


def test_hash_multi_thread(files: list) -> None:
    start = perf_counter()
    thread_map(
        get_hash,
        files,
        repeat("sha256"),
        max_workers=80,
        chunksize=15,
        desc="hashing files",
    )
    finish = perf_counter()
    return finish - start


def test_hash_multi_process(files: list) -> int:
    start = perf_counter()
    process_map(
        get_hash,
        files,
        repeat("sha256"),
        max_workers=80,
        chunksize=15,
        desc="hashing files",
    )
    finish = perf_counter()
    return finish - start


@perf_test.command()
@click.option("--path", "-p", type=click.Path())
@click.option("--trials", "-t", type=click.INT, default=2)
def test_hashes_multi_process_vs_thread(path: Path, trials: int) -> None:
    funcs = [test_hash_multi_thread, test_hash_multi_process]

    max_fun_nam = max([len(fun.__name__) for fun in funcs])
    files = get_files(path)
    stats = dict()

    for _ in range(trials):
        for fun in funcs:
            if fun.__name__ not in stats.keys():
                stats[fun.__name__] = list()
            result = fun(files)
            stats[fun.__name__].append(result)

    os.system("clear")
    for func, result in stats.items():
        print(f"{func.ljust(max_fun_nam)} was run for {trials=}, stats: {describe(result, 5)} seconds")
