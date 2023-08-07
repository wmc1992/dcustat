#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time

from blessed import Terminal

from .core import new_query
from dcustat import __version__


def print_dcu_stat(debug=False, *args, **kwargs):
    """
    Display the DCU query results into standard output.
    """
    try:
        dcu_stat = new_query(*args, **kwargs)
    except Exception as e:
        sys.stderr.write("获取 DCU 设备信息报错。请在参数中添加上 \"--debug\" 获取报错的详情信息；"
                         "并将报错信息反馈到：https://github.com/wmc1992/dcustat\n")
        if debug:
            try:
                import traceback
                traceback.print_exc(file=sys.stderr)
            except Exception:
                raise e
        sys.exit(1)

    dcu_stat.print_formatted(sys.stdout, **kwargs)


def loop_dcu_stat(interval=1.0, *args, **kwargs):
    term = Terminal()

    with term.fullscreen():
        while 1:
            try:
                query_start = time.time()

                # Move cursor to (0, 0) but do not restore original cursor loc
                print(term.move(0, 0), end="")
                print_dcu_stat(eol_char=term.clear_eol + os.linesep, *args, **kwargs)
                print(term.clear_eos, end="")

                query_duration = time.time() - query_start
                sleep_duration = interval - query_duration
                if sleep_duration > 0:
                    time.sleep(sleep_duration)
            except KeyboardInterrupt:
                return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", "--watch", nargs="?", type=float, default=0,
                        help="动态刷新模式；INTERVAL为刷新间隔，单位：秒；默认每2秒刷新一次；")
    parser.add_argument("--light", action="store_true", default=False,
                        help="使用较亮的模式显示，如果显示器渲染出来的结果较暗，可以打开该参数；")
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Debug模式时允许在程序出错的情况下打印更多的调试信息；")
    parser.add_argument("-v", "--version", action="version", version=("dcustat version: %s" % __version__))
    args = parser.parse_args()

    if args.interval is None:  # with default value
        args.interval = 2.0  # 默认每2秒刷新一次
    if args.interval > 0:
        args.interval = max(1, args.interval)
        loop_dcu_stat(**vars(args))
    else:
        del args.interval
        print_dcu_stat(**vars(args))


if __name__ == "__main__":
    main()
