from time import perf_counter
import click
from tqdm.contrib.concurrent import process_map
from itertools import repeat
from duple.__version__ import __version__
from duple.library import (
    get_available_hashes,
    timed_get_hash,
    get_max_workers,
    gen_test_files,
    tree,
    generate_options_list,
    create_output,
    remove_empty_directories,
    duple_outputs_exist,
    get_delete_paths,
    get_latest_file,
    follow_log,
    delete_logs,
)
import os
from pathlib import Path
import sys
from collections import Counter
from tqdm import tqdm
from duple.files import Files
from send2trash import send2trash
from humanize import naturalsize
from duple.app_logging import setup_logging, logger
from duple.decorators import log_func_with_args, log_func_start_finish_flags
from duple.info import LOGS_PATH

"""
To Do:
1. Add filtering capability for files (only pictures or files after a certain date)
2. Add StdIn support for scan
"""
"""
Only click interface functions will be in this file
"""


@click.group()
def cli():
    setup_logging()
    pass


@cli.command()
def wherelog():
    """print the path to the logs"""
    click.secho(f"{get_latest_file(LOGS_PATH, filter = '.jsonl')}")


@cli.command()
@click.option(
    "--level",
    "-l",
    type=click.STRING,
    default="DEBUG",
    help="Will only show specified level of log messages (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option("--filter", "-f", type=click.STRING, default=None)
def followlog(level: str = "DEBUG", filter: str = None):
    """follow the log until user interupts (ctrl-c), (just like "tail -f")"""

    while True:
        try:
            follow_log(level, filter)
        except:  # noqa E722
            pass


@cli.command()
def reset_logs():
    """empty the log files"""
    delete_logs()


@cli.command()
@click.argument("path", type=click.STRING)
@log_func_start_finish_flags
def hash_stats(path: str):
    """
    report hashing times for each available hashing algorithm on the specified file

    Args:
        path (str): path to file to hash
    """
    hashes = get_available_hashes()
    max_len_hash = max([len(hash) for hash in hashes]) + 2

    hash_times = process_map(
        timed_get_hash, hashes, repeat(path), max_workers=get_max_workers(), chunksize=1, desc="Hashing Files..."
    )

    hash_times = {k: v for k, v in hash_times}
    hash_times = sorted(hash_times.items(), key=lambda x: x[1])

    click.echo("Order = fastest > slowest")
    for hash, elapsed_time in hash_times:
        click.echo(f"{hash.ljust(max_len_hash)} {elapsed_time :8.6f} sec")


@cli.command()
@click.option(
    "--test_path", "-tp", type=click.Path(), default=os.getcwd(), help="path where the test directories will be created"
)
@click.option(
    "--number_of_directories", "-nd", type=click.INT, default=3, help="number of directories to make for the test"
)
@click.option(
    "--number_of_files",
    "-nf",
    type=click.INT,
    default=3,
    help="number of files to make in each top level directory, spread across the directories",
)
@click.option("--max_file_size", "-fs", type=click.INT, default=1024, help="file size to create in bytes")
@click.option("--print_tree", "-pt", is_flag=True, help="print tree with results")
@log_func_start_finish_flags
def make_test_files(
    test_path: Path, number_of_directories: int, number_of_files: int, max_file_size: int, print_tree: bool = False
):
    """make test files to learn or test with duple"""
    test_path = Path(test_path)
    gen_test_files(test_path, number_of_directories, number_of_files, max_file_size)

    if print_tree:
        click.secho()
        for line in tree(test_path):
            prefix_pointer_style = click.style("".join(line[:2]), fg="white")
            if line[-1]:
                name_style = click.style(line[2], fg="cyan")
            else:
                name_style = click.style(line[2], fg="white")
            click.secho(prefix_pointer_style + name_style)
        click.secho()


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="be more verbose during execution")
@click.option("--dry_run", "-dr", is_flag=True, help="Perform dry run, do everything except deleting files")
@click.option("--leave_empty_dirs", "-led", is_flag=True, help="Do not delete empty directories/folders")
@log_func_start_finish_flags
def rm(verbose: bool, dry_run: bool, leave_empty_dirs: bool) -> None:
    """
    rm sends all 'duplicate' files specified in duple.delete to the trash folder
    """
    logger.debug('Starting "duple rm"')

    message_margin = 16
    path = Path(os.getcwd())

    if not duple_outputs_exist(path):
        logger.debug('duple.delete does not exist, exiting "duple rm"')
        return

    files = get_delete_paths(path)

    delete_style = ""
    keep_style = ""

    if verbose:
        delete_style = click.style("deleted".ljust(message_margin), fg="yellow")
        keep_style = click.style("kept".ljust(message_margin), fg="green")

    if dry_run:
        delete_style = click.style("will delete".ljust(message_margin), fg="yellow")
        keep_style = click.style("will keep".ljust(message_margin), fg="green")
        verbose = True

    if not verbose:
        for file, data in tqdm(files.items()):
            if data["type"] == "DUPLICATE" and Path(file).exists():
                send2trash(file)

    if verbose:
        for i, (file, data) in enumerate(files.items()):
            completion_style = click.style(f"[{(i / len(files.items()) * 100) : 6.1f}%]", fg="cyan")

            if not dry_run and Path(file).exists() and data["type"] == "DUPLICATE":
                send2trash(file)

            if dry_run or verbose:
                if data["type"] == "ORIGINAL":
                    click.secho(f'{completion_style} {keep_style} {data["size"]}{file}')
                if data["type"] == "DUPLICATE":
                    click.secho(f'{completion_style} {delete_style} {data["size"]}{file}')

    if not dry_run and not leave_empty_dirs:
        remove_empty_directories(path, verbose)


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.STRING,
    default=str(),
    help="path to look in for duplicates, if this option is present, paths is ignored",
)
@click.option(
    "--paths_file_stdin",
    "-in",
    type=click.File("r"),
    default=sys.stdin,
    help="either a file containing a list of paths to evaluate or stdin",
)
@click.option(
    "--hash",
    "-h",
    type=click.STRING,
    default="sha256",
    help=f"the hashalgorithm to use, default = sha256, allowed alogorithsm: {get_available_hashes()}",
)
@click.option("--depth_min", "-d", is_flag=True, help="keep the file with the lowest pathway depth")
@click.option("--depth_max", "-D", is_flag=True, help="keep the file with the highest pathway depth")
@click.option("--name_min", "-n", is_flag=True, help="keep the file with the shortest name")
@click.option("--name_max", "-N", is_flag=True, help="keep the file with the longest name")
@click.option("--created_min", "-c", is_flag=True, help="keep the file with the oldest creation date")
@click.option("--created_max", "-C", is_flag=True, help="keep the file with the newest creation date")
@click.option("--modified_min", "-m", is_flag=True, help="keep the file with the oldest modified date")
@click.option("--modified_max", "-M", is_flag=True, help="keep the file with the newest modified, date")
@click.option("--accessed_min", "-a", is_flag=True, help="keep the file with the oldest accessed, date")
@click.option("--accessed_max", "-A", is_flag=True, help="keep the file with the newest accessed, date")
@click.option(
    "--number_of_cpus", "-ncpu", type=click.INT, default=get_max_workers(), help="maximum number of cpu cores to use"
)
@click.option("--chunksize", "-ch", type=click.INT, default=2, help="chunksize to give to workers, minimum of 2")
@log_func_start_finish_flags
@log_func_with_args
def scan(
    path: str,
    paths_file_stdin: click.File,
    hash: str,
    depth_min: bool,
    depth_max: bool,
    name_min: bool,
    name_max: bool,
    created_min: bool,
    created_max: bool,
    modified_min: bool,
    modified_max: bool,
    accessed_min: bool,
    accessed_max: bool,
    number_of_cpus: int = get_max_workers(),
    chunksize: int = 2,
) -> None:
    """
    Scan recursively computes a hash of each file and puts the hash into
    a dictionary.  The keys are the hashes of the files, and the values
    are the file paths and metadata.  If an entry has more than 1 file
    associated, they are duplicates.  The original is determined by the
    flags or options (ex: -d).  The duplicates are added to a file called
    duple.delete.
    """
    start = perf_counter()

    # input validation
    hashes = get_available_hashes()
    if hash not in hashes:
        click.secho(f"Hash must be one of the following: {hashes}")
        return

    if number_of_cpus == 0 or number_of_cpus > os.cpu_count():
        number_of_cpus = get_max_workers()
        click.echo(f"Invalid number_of_cpus, using {number_of_cpus}")

    if chunksize < 2:
        chunksize = 2
        click.secho(f"chunksize too low, setting to default of {chunksize}")

    flags = [
        depth_min,
        depth_max,
        name_min,
        name_max,
        accessed_min,
        accessed_max,
        created_min,
        created_max,
        modified_min,
        modified_max,
    ]

    c = Counter(flags)
    if c[True] == 0:
        click.secho("Must select at least one flag to determine handling of duplicates, ex: -d")

    if depth_min and depth_max:
        click.secho(f"{depth_min=} and {depth_max=}, Only one depth flag (-d or -D) can be set")
        return

    if name_min and name_max:
        click.secho(f"{name_min=} and {name_max=}, Only one name flag (-n or -N) can be set")
        return

    if created_min and created_max:
        click.secho(f"{created_min=} and {created_max=}, Only one created flag (-c or -C) can be set")
        return

    if modified_min and modified_max:
        click.secho(f"{modified_min=} and {modified_max=}, Only one modified flag (-m or -M) can be set")
        return

    logger.debug("Finished input validation")

    summary_statistics = dict()
    summary_statistics["Total Files"] = ""
    summary_statistics["Ignored Files"] = ""
    summary_statistics["Duplicate Files"] = ""
    summary_statistics["Duplicate Groups"] = ""
    summary_statistics["Total Size (duplicates)"] = ""
    summary_statistics["Total Size (all files)"] = ""
    summary_statistics["Hash Algorithm"] = hash
    summary_statistics["File System Traversal Time (seconds)"] = ""
    summary_statistics["Pre-Processing Files Time (seconds)"] = ""
    summary_statistics["Hashing Time (seconds)"] = ""
    summary_statistics["Total Time (seconds)"] = ""
    summary_statistics["Duple Version"] = __version__
    summary_statistics["Results Written To"] = ""
    summary_statistics["Total Time (seconds)"] = start

    # create filtering options list
    options = generate_options_list(flags)

    # file traversal
    summary_statistics["File System Traversal Time (seconds)"] = perf_counter()
    if path == "":
        path = os.getcwd()
        with paths_file_stdin:
            filelist = paths_file_stdin.read()
            filelist = filelist.split("\n")[:-1]
        logger.debug(f"Finished reading file list from stdin, {len(filelist)} files")
    else:
        filelist = list()
        for r, fds, fs in tqdm(os.walk(path, followlinks=False), desc="traversing file tree"):
            for f in fs:
                filelist.append(Path(r).joinpath(f).absolute())

        logger.debug(f"Finished reading files from os.walk, {len(filelist)} files")

    summary_statistics["File System Traversal Time (seconds)"] = (
        perf_counter() - summary_statistics["File System Traversal Time (seconds)"]
    )

    # create files
    summary_statistics["Pre-Processing Files Time (seconds)"] = perf_counter()
    files = Files(max_workers=number_of_cpus, chunksize=chunksize, hashalgo=hash)
    files.read_paths(filelist)
    summary_statistics["Pre-Processing Files Time (seconds)"] = (
        perf_counter() - summary_statistics["Pre-Processing Files Time (seconds)"]
    )

    # analyze duplicates
    summary_statistics["Hashing Time (seconds)"] = perf_counter()
    files.perform_analysis()
    logger.debug("Finished hashing")
    files.determine_originals(options)
    logger.debug("Finished selecting originals")
    summary_statistics["Hashing Time (seconds)"] = perf_counter() - summary_statistics["Hashing Time (seconds)"]

    summary_statistics["Total Files"] = files.file_count
    summary_statistics["Ignored Files"] = files.ignored_files
    summary_statistics["Duplicate Files"] = files.duplicate_file_count
    summary_statistics["Duplicate Groups"] = files.duplicate_group_count
    summary_statistics["Total Size (duplicates)"] = naturalsize(files.duplicate_file_size)
    summary_statistics["Total Size (all files)"] = naturalsize(files.total_file_size)
    summary_statistics["Total Time (seconds)"] = perf_counter() - summary_statistics["Total Time (seconds)"]
    summary_statistics["Results Written To"] = str(Path(path).joinpath("duple.delete").absolute())

    # create output
    create_output(
        options, path, files.create_duplicate_output(), files.create_ignored_files_output(), summary_statistics
    )
    logger.debug(f'Finished creating output, total "duple scan" time of {round(perf_counter() - start, 5): .5f}')


@log_func_with_args
@cli.command()
@log_func_start_finish_flags
def version():
    """display the current version of duple"""
    click.secho(f"duple version: {__version__}")
