#!/usr/bin/env python3

import argparse
import importlib
import os
import pathlib


def tool_fn(tool: str, func: str):
    return getattr(importlib.import_module(f'tools.{tool}'), func)


def supported_archs() -> tuple[str]:
    return tuple(d.name for d in pathlib.Path('storage').iterdir() if d.is_dir())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arch', '-A', required=True,
                        choices=supported_archs())

    subparsers = parser.add_subparsers(dest='subparser')

    for tool in pathlib.Path('tools').iterdir():
        if tool.is_file() and tool.suffix == '.py' and tool.stem != '__init__':
            subparser = subparsers.add_parser(tool.stem)
            tool_fn(tool.stem, 'args')(subparser)

    args, extra = parser.parse_known_args()
    arch = args.arch
    func = tool_fn(args.subparser, 'do')

    args = {k: v for k, v in vars(args).items()
            if k not in ('arch', 'subparser')}
    if extra and extra[0] == '--':
        args['extra'] = tuple(extra[1:])
    func(arch, **args)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    main()
