import cProfile
import functools
import pstats
from time import perf_counter
from uuid import uuid1
from duple.app_logging import logger, setup_logging

setup_logging()


def profile(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        try:
            retval = func(*args, **kwargs)
        finally:
            profiler.disable()
            with open("profile.out", "w") as profile_file:
                stats = pstats.Stats(profiler, stream=profile_file)
                stats.print_stats()
        return retval

    return inner


def log_func_with_args(func):
    start = perf_counter()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        funcname = f"{func.__module__}/{func.__qualname__}"
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"{funcname} called with args {signature}")
        try:
            logger.debug(f"{funcname} START", extra={"funcname": funcname})
            result = func(*args, **kwargs)
            logger.debug(f"{funcname} FINISH ({(perf_counter() - start): .5f})", extra={"funcname": funcname})
            return result
        except Exception as e:
            logger.exception(f"Exception raised in function {funcname}, exception: {str(e)}")
            raise e

    return wrapper


def log_func_time(func):
    start = perf_counter()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        funcname = f"{func.__module__}/{func.__qualname__}"
        try:
            logger.debug(f"{funcname} START")
            result = func(*args, **kwargs)
            logger.debug(
                f"{funcname} FINISH elapsed time: {(perf_counter() - start):.5f}", extra={"funcname": funcname}
            )
            return result
        except Exception as e:
            logger.exception(
                f"Exception raised in function {funcname}, exception: {str(e)}", extra={"funcname": funcname}
            )
            raise e

    return wrapper


def log_func_start_finish_flags(func):
    start_count = perf_counter()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        funcname = f"{func.__module__}/{func.__qualname__}"
        flag = "".ljust(20, "=")
        start = f"START {funcname}".center(40)
        finish = f"FINISH {funcname}".center(40)
        uid = uuid1().hex
        try:
            logger.info(f"{flag} {start} {flag} {uid=}", extra={"funcname": funcname})
            result = func(*args, **kwargs)
            logger.info(
                f"{flag} {finish} {flag} {uid=} elapsed time: {(perf_counter() - start_count):.5f} seconds",
                extra={"funcname": funcname},
            )

            return result
        except Exception as e:
            logger.exception(f"Exception raised in function {funcname}, exception: {str(e)}")
            raise e

    return wrapper
